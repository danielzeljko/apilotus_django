jQuery(document).ready(function ($) {
    let alert_types;
    let remove_sign = '<span class="glyphicon glyphicon-remove-sign" aria-hidden="true" style="color: #ffa5a5"></span>';
    let triangle_right = '<span class="glyphicon glyphicon-triangle-right" aria-hidden="true"></span>';
    let r = false;

    function get_alert_types() {
        $.ajax({
            type: "GET",
            url: "/alert/api/alert_type",
            data: {},
            success: function (response) {
                alert_types = response;
                let html = "";
                for (let i = 0; i < alert_types.length; i++) {
                    let alert_type = alert_types[i];
                    if (alert_type['status']) {
                        html += '<div id="atitle_' + alert_type['id'] + '" style="height:35px;padding-top:3px;border-bottom: 1px solid #e5e5e5;">';
                        html += '<button type="button" id="alert_' + alert_type['id'] + '" class="btn btn-link btn-sm btn_alert">' + triangle_right + "</button>";
                        html += '<span id="aname_' + alert_type['id'] + '" style="font-size:14px">' + alert_type['alert_name'] + " </span></div>";
                        html += '<div id="abody_' + alert_type['id'] + '" style="display:none;width:100%;padding-left:37px;padding-bottom:5px;border-bottom:1px solid #e5e5e5;">';
                        html += '<table class="table" style="padding:0;margin:0;border:none;background:#f9f2f4;">';
                        html += '<tbody id="acontent_' + alert_type['id'] + '"></tbody></table></div>';
                    }
                }
                $(".alert_body").html(html);
                get_alert_recent_list();
            },
            failure: function (status) {
            }
        });
    }

    function get_alert_recent_list() {
        $.ajax({
            type: "GET",
            url: "/alert/ajax_alert_recent_list",
            data: {},
            success: function (response) {
                let html = "";
                for (let i = 0; i < alert_types.length; i++) {
                    if (alert_types[i]['status'])
                        $("#acontent_" + alert_types[i]['id']).html("");
                }
                for (let i = 0; i < response.length; i++) {
                    html = "<tr>";
                    html += '<td style="border:none;padding:0;text-align:left;word-wrap: break-word;word-break:break-all;font-size:14px">';
                    html += "<b>" + response[i]['crm__crm_name'] + "</b>, ";
                    html += response[i]['level'] + " / " + response[i]['value'];
                    if (response[i]['from_date'] === response[i]['to_date']) {
                        html = html + ", Today";
                    } else {
                        html = html + (", " + response[i]['from_date'] + "  ~ " + response[i]['to_date']);
                    }
                    html += "</td>";
                    html += '<td style="border:none;padding:0;width:50px;text-align:right">';
                    html += '<button type="button" class="btn btn-link btn-sm btn_alert_delete" id="' + response[i]['id'] + '">' + remove_sign + "</button>";
                    html += "</td>";
                    html += "</tr>";
                    $("#acontent_" + response[i]['type']).append(html);
                }
                let total_count = 0;
                for (let i = 0; i < alert_types.length; i++) {
                    if (alert_types[i]['status']) {
                        let count = parseInt($("#acontent_" + alert_types[i]['id']).children().length);
                        if (count > 0) {
                            let alert_name = alert_types[i]['alert_name'] + " " + '<span style="padding:1px 5px 1px 5px;background:#e74b4e;color:#fff;border-radius:3px;">' + count + "</span>";
                            $("#aname_" + alert_types[i]['id']).html(alert_name);
                            total_count += count;
                        }
                        else {
                            $("#aname_" + alert_types[i]['id']).html(alert_types[i]['alert_name'] + " ");
                        }
                    }
                }
                if (0 === total_count) {
                    $(".span_alert_count").html("");
                } else {
                    $(".span_alert_count").html('<span class="alert_count">' + total_count + "</span>");
                }
            },
            failure: function (status) {
            }
        });
    }

    function delete_alert(alert_id) {
        $.ajax({
            type: "GET",
            url: "/alert/ajax_alert_delete",
            data: {
                alert_id: alert_id
            },
            success: function () {
                get_alert_recent_list();
            },
            failure: function () {
            }
        });
    }

    function alert_delete_all() {
        $.ajax({
            type: "GET",
            url: "/alert/ajax_alert_delete_all",
            data: {},
            success: function () {
                get_alert_recent_list();
            },
            failure: function () {
            }
        });
    }


    $("#alert_link").click(function () {
        if (r = !r) {
            $(".alert_body").html('<div style="text-align:center"><img src="/static/images/loading.gif" style="width:40px"></div>');
            $(".dropdown_content").slideDown();
            get_alert_types();
        } else {
            $(".dropdown_content").slideUp();
        }
    });
    $(".alert_body").on("click", ".btn_alert", function () {
        let conid = $(this).prop("id").substring(6);
        if (-1 != $(this).html().indexOf("glyphicon-triangle-bottom")) {
            $(this).html(triangle_right);
            $("#abody_" + conid).slideUp("1000", function () {
                $("#atitle_" + conid).css("border-bottom", "1px solid #e5e5e5");
                $("#atitle_" + conid).css("background", "white");
                $("#abody_" + conid).css("background", "white");
                $("#acontent_" + conid).css("background", "white");
            });
        } else {
            $(this).html('<span class="glyphicon glyphicon-triangle-bottom" aria-hidden="true" style="color: #ffa5a5"></span>');
            $("#abody_" + conid).slideDown("1000");
            $("#atitle_" + conid).css("border-bottom", "none");
            $("#atitle_" + conid).css("background", "#fff");
            $("#abody_" + conid).css("background", "#fff");
            $("#acontent_" + conid).css("background", "#fff");
        }
    });
    $(".alert_body").on("click", ".btn_alert_delete", function () {
        delete_alert($(this).prop("id"));
    });
    $(".btn_alert_delete_all").click(function () {
        $("#alert_delete_all_modal").modal("toggle");
    });
    $(".modal_btn_alert_delete_all").click(function () {
        $("#alert_delete_all_modal").modal("toggle");
        alert_delete_all();
    });
});
