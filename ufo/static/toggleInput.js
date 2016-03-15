Polymer({
  is: "ufo-toggle-input",
  properties: {
    inputName: {
      type: String
    },
    buttonText: {
      type: String
    },
    checked: {
      type: Boolean,
      value: false
    }
  },
  listeners: {
    'change': 'flipHiddenInput'
  },
  flipHiddenInput: function(e) {
    var toggleElem = event.path[0];
    var hiddenInput = this.$.hiddenToggle;
    hiddenInput.value = toggleElem.checked;
  }
});
