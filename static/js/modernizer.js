/*! modernizr 3.6.0 (Custom Build) | MIT *
 * https://modernizr.com/download/?-inputtypes !*/
!(function (e, t, n) {
  function o(e, t) {
    return typeof e === t;
  }
  function i() {
    var e, t, n, i, a, l, u;
    for (var c in s)
      if (s.hasOwnProperty(c)) {
        if (
          ((e = []),
          (t = s[c]),
          t.name &&
            (e.push(t.name.toLowerCase()),
            t.options && t.options.aliases && t.options.aliases.length))
        )
          for (n = 0; n < t.options.aliases.length; n++)
            e.push(t.options.aliases[n].toLowerCase());
        for (i = o(t.fn, 'function') ? t.fn() : t.fn, a = 0; a < e.length; a++)
          (l = e[a]),
            (u = l.split('.')),
            1 === u.length
              ? (Modernizr[u[0]] = i)
              : (!Modernizr[u[0]] ||
                  Modernizr[u[0]] instanceof Boolean ||
                  (Modernizr[u[0]] = new Boolean(Modernizr[u[0]])),
                (Modernizr[u[0]][u[1]] = i)),
            r.push((i ? '' : 'no-') + u.join('-'));
      }
  }
  function a() {
    return 'function' != typeof t.createElement
      ? t.createElement(arguments[0])
      : c
      ? t.createElementNS.call(t, 'http://www.w3.org/2000/svg', arguments[0])
      : t.createElement.apply(t, arguments);
  }
  var s = [],
    l = {
      _version: '3.6.0',
      _config: {
        classPrefix: '',
        enableClasses: !0,
        enableJSClass: !0,
        usePrefixes: !0,
      },
      _q: [],
      on: function (e, t) {
        var n = this;
        setTimeout(function () {
          t(n[e]);
        }, 0);
      },
      addTest: function (e, t, n) {
        s.push({ name: e, fn: t, options: n });
      },
      addAsyncTest: function (e) {
        s.push({ name: null, fn: e });
      },
    },
    Modernizr = function () {};
  (Modernizr.prototype = l), (Modernizr = new Modernizr());
  var r = [],
    u = t.documentElement,
    c = 'svg' === u.nodeName.toLowerCase(),
    f = a('input'),
    p = 'search tel url email datetime date month week time datetime-local number range color'.split(
      ' '
    ),
    d = {};
  (Modernizr.inputtypes = (function (e) {
    for (var o, i, a, s = e.length, l = '1)', r = 0; s > r; r++)
      f.setAttribute('type', (o = e[r])),
        (a = 'text' !== f.type && 'style' in f),
        a &&
          ((f.value = l),
          (f.style.cssText = 'position:absolute;visibility:hidden;'),
          /^range$/.test(o) && f.style.WebkitAppearance !== n
            ? (u.appendChild(f),
              (i = t.defaultView),
              (a =
                i.getComputedStyle &&
                'textfield' !== i.getComputedStyle(f, null).WebkitAppearance &&
                0 !== f.offsetHeight),
              u.removeChild(f))
            : /^(search|tel)$/.test(o) ||
              (a = /^(url|email)$/.test(o)
                ? f.checkValidity && f.checkValidity() === !1
                : f.value != l)),
        (d[e[r]] = !!a);
    return d;
  })(p)),
    i(),
    delete l.addTest,
    delete l.addAsyncTest;
  for (var m = 0; m < Modernizr._q.length; m++) Modernizr._q[m]();
  e.Modernizr = Modernizr;
})(window, document);
