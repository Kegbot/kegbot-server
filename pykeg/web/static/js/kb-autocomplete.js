$(document).ready(function() {
  var beverages = new Bloodhound({
    datumTokenizer: function(d) { return Bloodhound.tokenizers.whitespace(d.tokens.join(' ')); },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: beverage_complete_url + "?q=%QUERY"
  });
  beverages.initialize();

  $('.beer-select').each(function() {
    var beverage_name = $(this).find('input[name=beverage_name]');
    var beverage_id = $(this).find('input[name=beverage_id]');
    var producer_name = $(this).find('input[name=producer_name]');
    var producer_id = $(this).find('input[name=producer_id]');
    var style = $(this).find('input[name=style_name]');

    beverage_name.typeahead(null, {
      name: 'beverage',
      source: beverages.ttAdapter(),
      displayKey: 'name',
      templates: {
        suggestion: Handlebars.compile(
          '<p><strong>{{name}}</strong> ({{producer_name}})'
        )
      }
    });

    beverage_name.bind('typeahead:selected', function(obj, datum, name) {
      producer_name.val(datum.producer_name);
      producer_id.val(datum.producer_id);
      style.val(datum.style);
      beverage_id.val(datum.id);
    });
  });

  var users = new Bloodhound({
    datumTokenizer: function(d) { return Bloodhound.tokenizers.whitespace(d.tokens.join(' ')); },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: user_complete_url + "?q=%QUERY"
  });
  users.initialize();

  $('.user-select').each(function() {
    var username = $(this).find('input[name=username]');
    username.typeahead(null, {
      name: 'user',
      displayKey: 'username',
      source: users.ttAdapter(),
      templates: {
        suggestion: Handlebars.compile(
          '<p><strong>{{username}}</strong> ({{email}})</p>'
        )
      }
    });
  });
});
