$(document).ready(function () {
    $('.lpbm-collapser-button').click(function () {
      $('> .lpbm-collapser-button-elapse', this).toggle();
      $('> .lpbm-collapser-button-collapse', this).toggle();
      $('> .lpbm-collapser-body', $(this).parent().parent()).toggle();
    });
});
