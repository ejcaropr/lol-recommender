function init(data){
  if (data == null){
    data = [];
  }
  $.post("/load_table", data, function(resp){
    $(".container").html(resp);

    $("#sortable1, #sortable2").sortable({
        connectWith: ".connectedSortable"}).disableSelection();

    $("#sortable1").sortable({
      update: function(event, ui){
        /*$(this).sortable('refresh');*/
        var data = $(this).sortable('serialize');
        init(data);
      }
    });
  })
}

