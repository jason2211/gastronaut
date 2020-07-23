"""Models for Gastronaut."""
from datetime import datetime
from flask_bcrypt import Bcrypt
from types import SimpleNamespace
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()

DEFAULT_USER_IMAGE = "/static/images/default_user_icon.jpg"
DEFAULT_BANNER_IMAGE = "/static/images/horizon___widescreen_wallpaper_by_hameed.jpg"  # NOQA E501
DEFAULT_PREFERENCES = SimpleNamespace(show_alcohol=True)


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User model"""

    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    email = db.Column(db.String(320), nullable=False, unique=True, index=True)

    username = db.Column(db.String(30), nullable=False, unique=True)

    password = db.Column(db.String, nullable=False)

    avatar_url = db.Column(db.String, nullable=True)

    banner_url = db.Column(db.String, nullable=True)

    byline = db.Column(db.String(200), nullable=True, default='')

    bio = db.Column(db.String(500), nullable=True, default='')

    city = db.Column(db.String(50), nullable=False, default='')

    state = db.Column(db.String(50), nullable=False, default='')

    country = db.Column(db.String(50), nullable=False, default='')

    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    preferences = db.Column(db.PickleType, default=DEFAULT_PREFERENCES,
                            nullable=False)

    missions = db.relationship('Mission', secondary='users_missions',
                               backref='users')

    user_missions = db.relationship('UserMission', backref='user',
                                    cascade='all, delete-orphan')
    # missions user owns and can edit
    my_missions = db.relationship('Mission', backref='user')

    reports = db.relationship('Report', backref='user')

    @classmethod
    def register(cls, email, username, password):
        """Create and return a new user instance with hashed password."""

        hashed_utf8 = bcrypt.generate_password_hash(password).decode("utf8")

        user = cls(email=email, username=username, password=hashed_utf8)
        db.session.add(user)
        db.session.commit()

        user.add_bookmarks()

        return user

    def add_bookmarks(self):
        """Add a default bookmarks mission for user."""

        m = Mission.create(editor=self.id, name='Bookmarks', country='XX')
        self.missions.append(m)
        db.session.commit()

    @classmethod
    def authenticate(cls, email, password):
        """Return a user instance if credentials are as expected."""

        u = cls.query.filter_by(email=email).first()
        if not u:
            # return None for no email match in database
            return None

        if bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False

    @property
    def get_avatar(self):
        """Return photo_url if set else default image"""
        return self.avatar_url or DEFAULT_USER_IMAGE

    @property
    def get_banner(self):
        """Return photo_url if set else default image"""
        return self.banner_url or DEFAULT_BANNER_IMAGE

    @classmethod
    def set_get(self):
        """
        Return list of attributes for normal
        serialization, obj creation and editing.
        """
        return ['username', 'email', 'avatar_url', 'city', 'state']

    def serialize(self):
        """Serialize model set_get properties data to a dictonary."""
        # update model from database so serialization works by calling self.id
        id = self.id
        out = {k: v for k, v in self.__dict__.items() if k in self.set_get()}
        out['id'] = id
        return out

    def __repr__(self):
        """User representation"""
        return f"<User id={self.id} username={self.username} >"


class Mission(db.Model):
    """Mission model"""

    __tablename__ = 'missions'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    editor = db.Column(db.Integer, db.ForeignKey(User.id))

    name = db.Column(db.String(50), nullable=False)

    description = db.Column(db.String(100), nullable=True)

    is_public = db.Column(db.Boolean, default=False)

    date_shared = db.Column(db.DateTime, nullable=True)

    city = db.Column(db.String(50), index=True, nullable=True)

    state = db.Column(db.String(2), index=True, nullable=True)

    country = db.Column(db.String(2), nullable=False)

    likes = db.Column(db.PickleType, nullable=False, default={0})

    user_missions = db.relationship('UserMission', backref='mission',
                                    cascade='all, delete-orphan')

    businesses = db.relationship('Business', secondary='missions_businesses',
                                 backref='missions')

    mission_businesses = db.relationship(
        'MissionBusiness', cascade='all, delete-orphan')

    reports = db.relationship('Report', backref='mission')

    __table_args__ = (
        db.Index('order_date_shared_desc', date_shared.desc(),
                 postgresql_using='btree',
                 postgres_ops={'date_shared': 'DESC'}),
        db.Index('name_like', 'name', postgres_ops={
                 'name': 'text_pattern_ops'}),
    )

    def share(self):
        """Make mission public and add current datime."""

        self.is_public = True
        self.date_shared = datetime.now()

    @classmethod
    def get_by_recent(cls, offset):
        """Return misions by most recent"""
        return cls.query.filter(cls.is_public == True).order_by(  # NOQA E712
            cls.date_shared.desc()).offset(offset).limit(50).all()

    @classmethod
    def search(cls, params):
        """Return misions by search criteria."""

        order_by_dict = {
            'recent': Mission.date_shared.desc(),
            'oldest': Mission.date_shared.asc(),
            'likes': Mission.likes.desc(),
        }

        city = params['city']
        state = params['state']
        country = params['country']
        sort = params['sort_by']
        keywords = params['keywords']

        return db.session.query(
            Mission).join(
                MissionBusiness).join(
                    Business).filter(db.and_(
                        Mission.is_public == True,  # NOQA E712
                        db.or_(
                            db.and_(
                                Business.city.ilike(f'%{city}%'),
                                Business.state.ilike(f'%{state}%'),
                                Business.country.ilike(f'%{country}%')
                            ),
                            db.and_(
                                Mission.city.ilike(f'%{city}%'),
                                Mission.state.ilike(f'%{state}%'),
                                Mission.country.ilike(f'%{country}%')
                            )
                        ),
                        db.or_(
                            *cls.make_keyword_statements(keywords)
                        )
                    )).order_by(order_by_dict[sort]).all()

    @classmethod
    def make_keyword_statements(cls, keywords):

        # keywords is the whole statement plus each word
        keywords = [keywords, *[w for w in keywords.strip().split(' ')]]

        statements = [
            [Mission.name.ilike(f'%{keyword}%'),
             Mission.description.ilike(f'%{keyword}%'),
             Business.name.ilike(f'%{keyword}%')]
            for keyword in keywords]

        out = []
        [out.extend(s) for s in statements]

        return out

    @classmethod
    def set_get(self):
        """
        Return list of attributes for normal
        serialization, obj creation and editing.
        """
        return ['editor', 'name', 'city', 'state', 'country', 'likes']

    def serialize(self):
        """Serialize model set_get properties data to a dictonary."""
        # update model from database so serialization works by calling self.id
        id = self.id
        out = {k: v for k, v in self.__dict__.items() if k in self.set_get()}
        out['id'] = id
        return out

    @classmethod
    def create(cls, **kwargs):
        """Return a new instance of Mission that has been added to session."""
        try:
            m = cls(**kwargs)
        except Exception:
            return False

        db.session.add(m)
        return m

    def __repr__(self):
        """Mission representation."""
        m = self
        return f"<Mission id={m.id} name={m.name} editor={m.editor} >"


class UserMission(db.Model):
    """User-Mission Model."""

    __tablename__ = 'users_missions'

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)

    mission_id = db.Column(
        db.Integer, db.ForeignKey(Mission.id), primary_key=True)

    mission_completed = db.Column(db.Boolean, default=False)

    goals_completed = db.Column(db.PickleType, default=[])

    __mapper_args__ = {
        'confirm_deleted_rows': False
    }

    @classmethod
    def get_user_mission(cls, user_id, mission_id):
        """Return UserMission with given user_id/mission id."""

        u_m = cls.query.filter_by(
            user_id=user_id, mission_id=mission_id).first()

        return u_m

    @classmethod
    def create(cls, **kwargs):
        """
        Return a new instance of UserMission
        that has been added to session.
        """
        try:
            u_m = cls(**kwargs)

        except Exception:
            return False

        db.session.add(u_m)
        return u_m

    def __repr__(self):
        """UserMission representation"""
        u = self
        return f"<UserMission user_id={u.user_id} mission_id={u.mission_id} >"  # NOQA E501


class Business(db.Model):
    """Business Model for Yelp businesses"""

    __tablename__ = 'businesses'

    id = db.Column(db.String, primary_key=True)

    longitude = db.Column(db.Float, nullable=False)

    latitude = db.Column(db.Float, nullable=False)

    name = db.Column(db.String(), nullable=False)

    city = db.Column(db.String(50), nullable=False)

    state = db.Column(db.String(2), nullable=False)

    country = db.Column(db.String(2), nullable=False)

    reports = db.relationship('Report', backref='business')

    missions_businesses = db.relationship('MissionBusiness',
                                          cascade='all, delete-orphan')

    @classmethod
    def create(cls, **kwargs):
        """Return a new instance of Business that has been added to session."""
        try:
            b = cls(**kwargs)
        except Exception:
            return False

        db.session.add(b)
        return b


class Report(db.Model):
    """Mission Report Model."""

    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    mission_id = db.Column(
        db.Integer, db.ForeignKey(Mission.id), nullable=True)

    business_id = db.Column(
        db.String, db.ForeignKey(Business.id), nullable=True)

    submitted_on = db.Column(db.DateTime, default=datetime.utcnow())

    text = db.Column(db.Text, nullable=False)

    likes = db.Column(db.PickleType, nullable=False, default={0})

    @classmethod
    def get_by_recent(cls, offset):
        """Return reports by most recent."""
        return cls.query.order_by(
            cls.submitted_on.desc()).offset(offset).limit(50).all()

    @classmethod
    def search(cls, params):
        """Return reports by search criteria."""

        order_by_dict = {
            'recent': Report.submitted_on.desc(),
            'oldest': Report.submitted_on.asc(),
            'likes': Report.likes.desc(),
        }

        city = params['city']
        state = params['state']
        country = params['country']
        sort = params['sort_by']
        keywords = params['keywords']

        return db.session.query(
            Report).outerjoin(
                Business).outerjoin(
                    Mission).filter(db.and_(
                        db.or_(
                            db.and_(
                                Business.city.ilike(f'%{city}%'),
                                Business.state.ilike(f'%{state}%'),
                                Business.country.ilike(f'%{country}%')
                            ),
                            db.and_(
                                Mission.city.ilike(f'%{city}%'),
                                Mission.state.ilike(f'%{state}%'),
                                Mission.country.ilike(f'%{country}%')
                            )
                        ),
                        db.or_(
                            *cls.make_keyword_statements(keywords)
                        )
                    )).order_by(order_by_dict[sort]).all()

    @classmethod
    def make_keyword_statements(cls, keywords):

        # keywords is the whole statement plus each word
        keywords = [keywords, *[w for w in keywords.strip().split(' ')]]

        statements = [
            [Business.name.ilike(f'%{keyword}%'),
             Mission.name.ilike(f'%{keyword}%'),
             Report.text.ilike(f'%{keyword}%')]
            for keyword in keywords]

        out = []
        [out.extend(s) for s in statements]

        return out

    @classmethod
    def create(cls, **kwargs):
        """Return a new instance of Report that has been added to session."""
        try:
            r = cls(**kwargs)
        except Exception:
            return False

        db.session.add(r)
        return r


class MissionBusiness(db.Model):
    """Missions Businesses join table."""

    __tablename__ = 'missions_businesses'

    mission_id = db.Column(
        db.Integer, db.ForeignKey(Mission.id), primary_key=True)

    business_id = db.Column(
        db.String, db.ForeignKey(Business.id), primary_key=True)

    @classmethod
    def create(cls, **kwargs):
        """
        Return a new instance of MissionBusiness
        that has been added to session.
        """
        try:
            m_b = cls(**kwargs)
        except Exception:
            return False

        db.session.add(m_b)
        return m_b


# @property
    # def roles(self):
    #     """Return active roles, names, emails for project."""
    #     # With multiple querys
    #     # return [(pe.role, pe.employees.name, pe.employees.email, self.name)
    #     #         for pe in self.prod_employ]

    #     # With single query.
    #     return db.session.query(
    #         ProductEmployee.role, Employee.name, Employee.email, Product.name
    #     ).filter_by(product_id=self.id).join(Employee).join(Product).all()
