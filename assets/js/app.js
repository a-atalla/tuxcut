$(document).ready(function(){
  $.ajax({
    url: 'https://api.github.com/repos/a-atalla/tuxcut/releases',
    method: 'GET',
    success: function (data) {
      var totalCount = data[0].assets[0].download_count + data[0].assets[1].download_count
      $('#count').text(totalCount)
    }
  })

  // Update copyright year
  $('#copyright').text($('#copyright').text().replace('#YEAR#', new Date().getFullYear()))
})
