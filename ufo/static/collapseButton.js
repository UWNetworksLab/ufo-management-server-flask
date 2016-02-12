Polymer({
  is: "ufo-collapse-button",
  properties: {
    buttonText: {
      type: String
    },
    collapseText: {
      type: String
    },
    label: {
      type: String
    }
  },
  toggleCollapse: function(e){
    var target = e.target;
    var parent = target.parentElement;
    var collapse = parent.querySelector('iron-collapse.collapse');
    collapse.toggle();
  }
});
