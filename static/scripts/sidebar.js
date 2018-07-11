$(document).ready(function () {


    var dateToday = new Date();
    var dates = $(".fromm, .too").datepicker({
        defaultDate: "+1w",
        changeMonth: true,
        numberOfMonths: 3,
        minDate: dateToday,
        onSelect: function (selectedDate) {
            var option = this.id == "from" ? "minDate" : "maxDate",
                instance = $(this).data("datepicker"),
                date = $.datepicker.parseDate(instance.settings.dateFormat || $.datepicker._defaults.dateFormat, selectedDate, instance.settings);
            dates.not(this).datepicker("option", option, date);
        }
    });


    $(".from").datepicker({
        dateFormat: "dd-M-yy",
        minDate: 0,
        onSelect: function (date) {
            var date2 = $('.from').datepicker('getDate');
            date2.setDate(date2.getDate() + 1);
            $('.to').datepicker('setDate', date2);
            //sets minDate to dt1 date + 1
            $('.to').datepicker('option', 'minDate', date2);
        }
    });
    $(".to").datepicker({
        dateFormat: "dd-M-yy",
        onClose: function () {
            var dt1 = $('.from').datepicker('getDate');
            console.log(dt1);
            var dt2 = $('.to').datepicker('getDate');
            if (dt2 <= dt1) {
                var minDate = $('.to').datepicker('option', 'minDate');
                $('.to').datepicker('setDate', minDate);
            }
        }
    });


    // toggle sidebar when button clicked
    $('.sidebar-toggle').on('click', function () {
        $('.sidebar').toggleClass('toggled');
    });

    // auto-expand submenu if an item is active
    var active = $('.sidebar .active');

    if (active.length && active.parent('.collapse').length) {
        var parent = active.parent('.collapse');

        parent.prev('a').attr('aria-expanded', true);
        parent.addClass('show');
    }
});

$(document).on('click', '.btnClos', function () {
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth(); //January is 0!
    var mm2 = today.getMonth() + 3; //January is 0!
    var yyyy = today.getFullYear();

    //var minDate = dd - mm -
    //var maxDate = minDate +
});