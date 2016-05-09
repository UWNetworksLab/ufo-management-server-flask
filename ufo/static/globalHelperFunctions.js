var submitByFormId = function(formId) {
  document.getElementById(formId).submit();
};

var submitUsersManually = function() {
  var formId = 'users-manual-form';
  var formElem = document.getElementById(formId);
  var name = formElem.querySelector('#manualUserName').value;
  var email = formElem.querySelector('#manualUserEmail').value;
  var userArray = [];
  userArray.push({'name': name, 'email': email});
  var input = formElem.querySelector('#manualUserInput');
  input.value = JSON.stringify(userArray);
  formElem.submit();
};

/**
 * I had to do this outside of a custom element because of the way that the
 * browser handles permissions for using the document.execCommand and
 * clipboardData API's. In essence, it doesn't like how Polymer registers and
 * fire event handlers and won't let you touch clipboardData from there, thus
 * the Javascript is outside of Polymer.
 */
(function() {
  'use strict';
  document.body.addEventListener('copy', copyInviteCodeToClipboard, true);

  function copyInviteCodeToClipboard(e) {
    if (e.target !== document.body) {
      return;
    }
    e.preventDefault();

    var input = document.getElementById('hiddenCopyInput');
    e.clipboardData.setData('text/plain', input.value);
  }
})();
