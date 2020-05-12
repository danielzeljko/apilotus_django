jQuery(document).ready(function ($) {

    function get_selected_crm() {
        let crm_dropdown_list = $(".crm_dropdown_list");
        if (crm_dropdown_list.length > 0) {
            crm_id = crm_dropdown_list.prop("id");
            crm_name = crm_dropdown_list.html();
        }
    }

    function show_alert(alert) {
        let alert_box = $(".custom_alert");
        alert_box.html(alert);
        alert_box.fadeIn(1e3, function () {
            alert_box.fadeOut(3e3);
        });
    }

    function show_status(status_type, show_hide) {
        let waiting_box = $(".custom_waiting");
        if ("list" === status_type) {
            if (show_hide)
                waiting_box.html(loading_gif);
            else
                waiting_box.html("");
        }
    }

    function get_custom_report() {
        show_status("list", true);
        $(".table_body").html("");
        $("#id_head_sign").html(loading_gif);

        if (-1 === crm_id) {
            show_alert("Please select the CRM Account");
            return;
        }

        $.ajax({
            type: "GET",
            url: "/admin/ajax_custom_report",
            data: {
                crm_id: crm_id,
            },
            success: function (response) {
                show_status("list", false);
                $("#id_head_sign").html("");

                let total_length = response.results.length;
                if (0 === total_length)
                    return void show_alert("There is no information.");

                let html = "";
                for (let i = 0; i < total_length; i++) {
                    let prospect = response.results[i];

                    html += "<tr>";
                    html += "<td>" + (i + 1) + "</td>";
                    html += "<td>" + prospect['campaign_name'] + "</td>";
                    html += "<td>" + prospect['count_prospects'] + "</td>";
                    html += "<td>" + prospect['count_customers']['value'] + "</td>";
                    html += "<td>" + prospect['conversion_percent']['rendered'] + "</td>";
                    html += "<td>" + prospect['total_revenue']['html'] + "</td>";
                    html += "<td>" + prospect['average_revenue']['html'] + "</td>";
                    html += "</tr>";
                }
                $(".table_body").html(html);
            },
            failure: function () {
                show_alert("Cannot load custom report information.");
            }
        })
    }

    $(".crm_dropdown_menu li").on("click", function () {
        crm_name = $(this).text();
        crm_id = $(this).find("a").attr("id");
        $(".crm_toggle_button").html(crm_name + ' <span class="caret"></span>');
    });

    $(".btn_search").click(function () {
        get_custom_report();
    });

    let loading_gif = '<img src="/static/images/loading.gif" style="width: 22px; height: 22px;">';
    let crm_id = -1;
    let crm_name = "";

    get_selected_crm();
});
