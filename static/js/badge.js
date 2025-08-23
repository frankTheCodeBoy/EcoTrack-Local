document.addEventListener('DOMContentLoaded', function () {
  const badgeAlert = document.querySelector('.alert-success');
  if (badgeAlert) {
    badgeAlert.classList.add('animate__animated', 'animate__fadeInDown');
  }
});
