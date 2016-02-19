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
