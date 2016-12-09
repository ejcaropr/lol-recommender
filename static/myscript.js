function init(data){
  if (data == null){
    data = [];
  }

  $.post("/load_table", data, function(resp){
    $("#sortable2").html(resp);

    $("#sortable1, #sortable2").sortable({
        connectWith: ".connectedSortable"});

    $("#sortable1").sortable({
      update: function(event, ui){
        /*$(this).sortable('refresh');*/
        var data = $(this).sortable('serialize') + "&degree=" + $("#slider").slider("value");
        init(data);
      }
    });

    var handle = $( "#custom-handle" );
    $("#slider").slider({
      min: 10,
      max: 50,

      create: function() {
        handle.text($(this).slider("value")/10);
      },
      slide: function(event, ui){
        handle.text(ui.value/10);
      },
      stop: function(event, ui){
        var data = $("#sortable1").sortable('serialize') + "&degree=" + $(this).slider("value");
        init(data);
      }
    });

  })
}

