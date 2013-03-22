angular.module('kbNgFilters', ['ngSanitize']).
      filter('volume', function() {
      return function(input) {
        var ret = '<span class="hmeasure" title="' + input + ' mL">\n';
        ret += '  <span class="num">' + input + '</span>\n';
        ret += '  <span class="unit">mL</span>\n';
        ret += '</span>\n';
        return ret;
      }
  });
