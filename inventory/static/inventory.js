$(document).ready(function() {

    // $('#cpu a').click(function (e) {
    //     e.preventDefault();
    //     $(this).tab('show')
    // });
    //
    // $('#memory a').click(function (e) {
    //     e.preventDefault();
    //     $(this).tab('show')
    // });

    $(document).ready(function() {
        $('#table-computer, #table-cpu, #table-memory, #table-storage, #table-devices').DataTable();
    });
});