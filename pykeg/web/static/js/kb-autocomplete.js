$(document).ready(function() {
  var beverages = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace("value"),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: beverage_complete_url + "?q=%QUERY",
      wildcard: "%QUERY"
    }
  });
  // beverages.initialize();

  $(".beer-select").each(function() {
    var beverage_name = $(this).find("input[name=beverage_name]");
    var beverage_id = $(this).find("input[name=beverage_id]");
    var producer_name = $(this).find("input[name=producer_name]");
    var producer_id = $(this).find("input[name=producer_id]");
    var style = $(this).find("input[name=style_name]");

    beverage_name.typeahead(null, {
      name: "beverage",
      source: beverages,
      display: "name",
      templates: {
        suggestion: Handlebars.compile(
          "<p><strong>{{name}}</strong> ({{producer_name}})"
        )
      }
    });

    beverage_name.bind("typeahead:select", function(obj, datum, name) {
      producer_name.val(datum.producer_name);
      producer_id.val(datum.producer_id);
      style.val(datum.style);
      beverage_id.val(datum.id);
    });
  });

  var users = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace("value"),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: user_complete_url + "?q=%QUERY",
      wildcard: "%QUERY"
    }
  });

  $(".user-select").each(function() {
    var username = $(this).find("input[name=username]");
    username.typeahead(null, {
      name: "user",
      display: "username",
      source: users,
      templates: {
        suggestion: Handlebars.compile(
          "<p><strong>{{username}}</strong> ({{email}})</p>"
        )
      }
    });
  });
});
