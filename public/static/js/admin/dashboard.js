jQuery(document).ready(function(t) {
    let loading_gif = '<img src="/static/images/loading.gif" style="width: 22px; height: 22px;">';
    let remove_icon = '<span class="glyphicon glyphicon-remove-sign" aria-hidden="true" style="color: #ffa5a5"></span>';
    let dashboard_columns = "";
    let crm_positions = "";
    let crm_list = null;
    let selected_crm_id = -1;
    let alert_settings;
    let date_type = "date_thisweek";
    let from_date = "";
    let to_date = "";

    // for crm list
    let crm_table = jQuery('#a_crm_list_tb').DataTable( {
        searching: false,
        paging: false,
        bSort: false,
        info:false,
        fixedHeader: true,
        responsive: true
    } );

    function show_alert(type, content) {
        if (type === "sales") {
            t(".dashboard_sales_alert").html(content);
            t(".dashboard_sales_alert").fadeIn(1000, function() {
                t(".dashboard_sales_alert").fadeOut(3000)
            });
        }
        else if (type === "setting") {
            t(".setting_edit_alert").html(content);
            t(".setting_edit_alert").fadeIn(1000, function () {
                t(".setting_edit_alert").fadeOut(3000)
            });
        }
    }

    function show_waiting(type, crm_id, show) {
        if (type === "sales") {
            show ? t(".dashboard_sales_waiting").html(loading_gif) : t(".dashboard_sales_waiting").html("");
        }
        else if (type === "crm") {
            show ? (t("#crm1_" + crm_id + "_0").html(loading_gif),
                t("#crm2_" + crm_id + "_0").html(""),
                t("#crm3_" + crm_id + "_0").html(""),
                t("#crm4_" + crm_id + "_0").html(""),
                t("#crm5_" + crm_id + "_0").html(""),
                t("#crm6_" + crm_id + "_0").html(""),
                t("#crm61_" + crm_id + "_0").html(""),
                // t("#crm62_" + crm_id + "_0").html(""),
                t("#crm7_" + crm_id + "_0").html(""),
                t("#crm8_" + crm_id + "_0").html(""),
                t("#crm9_" + crm_id + "_0").html(""),
                t("#crm10_" + crm_id + "_0").html(""),
                t(".subrow_" + crm_id).each(function(e) {
                    t(this).remove()
                })) : t("#crm1_" + crm_id + "_0").html("");
        }
    }

    function show_headers() {
        if (dashboard_columns !== "") {
            let columns = dashboard_columns.split(",");
            for (let i = 1; i <= 8; i++) {
                t(".table_overall th:nth-child(" + i + ")").hide();
                t(".table_overall td:nth-child(" + i + ")").hide();
                t(".table_dashboard th:nth-child(" + (i + 3) + ")").hide();
                t(".table_dashboard td:nth-child(" + (i + 3) + ")").hide();

                for (let j = 0; j < columns.length; j++) {
                    if (i == columns[j]) {
                        t(".table_overall th:nth-child(" + i + ")").show();
                        t(".table_overall td:nth-child(" + i + ")").show();
                        t(".table_dashboard th:nth-child(" + (i + 3) + ")").show();
                        t(".table_dashboard td:nth-child(" + (i + 3) + ")").show();
                        break
                    }
                }
            }
        }
    }

    function show_result() {
        if ("" === t("#from_date").val()) {
            show_alert("sales", "Please select FROM DATE.");
            return;
        }
        else if ("" === t("#to_date").val()) {
            show_alert("sales", "Please select TO DATE.");
            return;
        }

        show_waiting("sales", "", true);
        t.ajax({
            type: "GET",
            url: "/admin/ajax_crm_list",
            data: {},
            success: function(response) {
                show_waiting("sales", "", false);
                crm_list = response;
                crm_table.clear().draw();
                t.ajax({
                    type: "GET",
                    url: "/admin/ajax_dashboard_sales_all",
                    data: {
                        from_date: t("#from_date").val(),
                        to_date: t("#to_date").val()
                    },
                    success: function(results) {
                        let tb_arr = [];

                        let position_ids = crm_positions.split(",");
                        for (let r = 0; r < position_ids.length; r++) {
                            let crm_id = parseInt(position_ids[r]);
                            let crm = crm_list.filter(item => item['id'] === crm_id)[0];
                            let sales = results.filter(item => item['crm_id'] === crm_id);
                            if (sales.length > 0) {
                                for (let i = 0; i < sales.length; i++) {
                                    let label_type = sales[i]['label_id'] == null ? 0 : sales[i]['label_id'];
                                    let label_name = sales[i]['label_name'];
                                    let crm_goal = sales[i]['label_id'] === null ? parseFloat(crm['sales_goal']) : parseFloat(sales[i]['goal']);

                                    let step1 = parseFloat(sales[i]['step1']);
                                    let step2 = parseFloat(sales[i]['step2']);
                                    let step1_nonpp = parseFloat(sales[i]['step1_nonpp']);
                                    let step2_nonpp = parseFloat(sales[i]['step2_nonpp']);
                                    let prepaid = parseFloat(sales[i]['prepaids']);
                                    let prepaid_step1 = parseFloat(sales[i]['prepaids_step1']);
                                    let prepaid_step2 = parseFloat(sales[i]['prepaids_step2']);
                                    let tablet = parseFloat(sales[i]['tablet_step1']);
                                    let tablet_step2 = parseFloat(sales[i]['tablet_step2']);
                                    let order_count = parseFloat(sales[i]['order_count']);
                                    let order_page = parseFloat(sales[i]['order_page']);
                                    let decline = parseFloat(sales[i]['declined']);
                                    let gross_order = parseFloat(sales[i]['gross_order']);
                                    let timestamp = sales[i]['updated_at'];

                                    let take_rate = (0 === step1) ? "0" : (100 * step2 / step1).toFixed(2);
                                    let tablet_p = (tablet + step2_nonpp === 0) ? "0" : (100 * tablet / (tablet + step2_nonpp)).toFixed(2);
                                    let order_p = (0 === order_count) ? "0" : (order_page / order_count).toFixed(2);
                                    let decline_p = (0 === gross_order) ? "0" : (decline / gross_order).toFixed(2);
                                    let s1pp = (0 === prepaid) ? "0" : (prepaid_step1 * 100 / prepaid).toFixed(2);
                                    let s2pp = (0 === prepaid) ? "0" : (prepaid_step2 * 100 / prepaid).toFixed(2);

                                    let progress_tag = '';
                                    let goal_tag = '';

                                    if (0 === label_type) {
                                        progress_tag = '<span id="crm9_' + crm_id + "_" + label_type + '"><div class="bar-main-container"><div id="bar_' + crm_id + '" class="bar-percentage">' + (crm_goal > 0.0 ? Math.round(100 * step1 / crm_goal) : 0) + '%</div><div class="bar-container"><div class="bar" style="width: ' + (crm_goal > 0.0 ? Math.round(100 * step1 / crm_goal) : 0 )+ '%"></div></div></div></span>';
                                        goal_tag += '<span id="crm10_' + crm_id + "_" + label_type + '">' + step1 + " / " + crm_goal + '</span>';
                                    }
                                    else {
                                        progress_tag = '<span id="crm9_' + crm_id + "_" + label_type + '">' + (crm_goal > 0.0 ? Math.round(100 * step1 / crm_goal) : 0) + ' %</span>';
                                        goal_tag = '<span id="crm10_' + crm_id + "_" + label_type + '">' + step1 + " / " + crm_goal + '</span>';
                                    }

                                    let no_tag = '';
                                    let crm_tag = '';
                                    let vertical_tag = '';
                                    let setting_btn = '';

                                    if (0 === label_type) {
                                        no_tag = '<span class="a_dsb_no_spn crm_row" id="row_' + crm_id + '">' + (r + 1) + '</span>';
                                        crm_tag = '<span data-toggle="tooltip" data-placement="bottom" id="ll' + crm_id + '" ' +
                                            'class="payment_badge payment_badge_blue crm_name_row a_sub_spn_vertical"' +
                                            ' title="' + timestamp + '">' + crm['crm_name'] + '</span>' +
                                            '<span class="a_less_than_390 a_less_than_390_tb">' + goal_tag + '</span>';
                                        vertical_tag = '<span id="crm0_' + crm_id + '_0">-</span>';
                                        setting_btn = '<button type="button" id="setting_' + crm_id + '" class="btn btn-link btn-sm btn_setting" data-toggle="modal" data-target="#setting_edit_modal"><span class="glyphicon glyphicon-list" aria-hidden="true"></span></button>';
                                    }
                                    else {
                                        no_tag = '<span class="a_sub_spn"></span>';
                                        crm_tag = '<span class="a_sub_spn a_sub_spn_vertical a_less_than_390">' + label_name + '&nbsp;</span>' +
                                            '<span class="a_less_than_390 a_less_than_390_tb">' + goal_tag + '</span>';
                                        vertical_tag = '<span id="crm0_' + sales[1] + "_" + label_type + '">' + label_name + '</span>';
                                        setting_btn = '';
                                    }
                                    let sub_arr = new Array(
                                        no_tag,
                                        crm_tag,
                                        vertical_tag,
                                        '<span id="crm1_' + crm_id + "_" + label_type + '">' + step1 + '</span>',
                                        '<span class="a_crm_td_none_dis" id="crm2_' + crm_id + "_" + label_type + '">' + step2 + '</span>',
                                        '<span id="crm3_' + crm_id + "_" + label_type + '">' + take_rate + '</span>',
                                        '<span id="crm4_' + crm_id + "_" + label_type + '">' + tablet + '</span>',
                                        '<span id="crm5_' + crm_id + "_" + label_type + '">' + tablet_p + '</span>',
                                        '<span id="crm6_' + crm_id + "_" + label_type + '">' + prepaid_step1 + '</span>',
                                        '<span class="a_crm_td_none_dis" id="crm7_' + crm_id + "_" + label_type + '">' + order_p + '</span>',
                                        '<span class="a_crm_td_none_dis" id="crm8_' + crm_id + "_" + label_type + '">' + decline_p + '</span>',
                                        '<span id="crm61_' + crm_id + "_" + label_type + '">' + s1pp + '</span>',
                                        progress_tag,
                                        goal_tag,
                                        setting_btn
                                        // '<button type="button" id="refresh_' + crm_id + '" class="btn btn-link btn-sm btn_refresh"><span class="glyphicon glyphicon-refresh" aria-hidden="true"></span></button>'
                                    );

                                    tb_arr.push(sub_arr);
                                }
                            }
                        }
                        for ( let k = 0; k < tb_arr.length; k ++ ) {
                            crm_table.row.add([
                                tb_arr[k][0],
                                tb_arr[k][1],
                                tb_arr[k][2],
                                tb_arr[k][3],
                                tb_arr[k][4],
                                tb_arr[k][5],
                                tb_arr[k][6],
                                tb_arr[k][7],
                                tb_arr[k][8],
                                tb_arr[k][9],
                                tb_arr[k][10],
                                tb_arr[k][11],
                                tb_arr[k][12],
                                tb_arr[k][13],
                                tb_arr[k][14],
                                // tb_arr[k][15],
                            ]).draw(false);
                        }
                        // tooltip in device add modal
                        jQuery('[data-toggle="tooltip"]').tooltip();
                        calculate_total();
                        // show_headers();

                        jQuery(".a_sub_spn").parent("td").addClass("a_no_border_top");
                        jQuery(".a_sub_spn_vertical").parent("td").addClass("a_border_right");
                        jQuery(".a_crm_td_none_dis").parent("td").addClass("g_none_dis");

                        // new jQuery.fn.dataTable.FixedHeader( crm_table );
                    },
                    failure: function(e) {
                        show_alert("sales", "Cannot load sales information.")
                    }
                })
            },
            failure: function() {
                show_waiting("sales", "", false);
                show_alert("sales", "Cannot load CRM site information.")
            }
        });
    }

    function calculate_total() {
        let count = 0;
        let step1 = 0;
        let step2 = 0;
        let tablet = 0;
        let tablet_percent = 0;
        let prepaids = 0;
        let order_percent = 0;
        let decline_percent = 0;
        let goal = 0;
        t(".crm_row").parent("td").parent("tr").each(function() {
            let crm_id = t(this).children("td:first-child").children(".crm_row").prop("id").substring(4);
            if (t("#crm1_" + crm_id + "_0").html()) {
                step1 += parseInt(t("#crm1_" + crm_id + "_0").html());
                step2 += parseInt(t("#crm2_" + crm_id + "_0").html());
                tablet += parseInt(t("#crm4_" + crm_id + "_0").html());
                tablet_percent += parseFloat(t("#crm5_" + crm_id + "_0").html());
                prepaids += parseInt(t("#crm6_" + crm_id + "_0").html());
                order_percent += parseFloat(t("#crm7_" + crm_id + "_0").html());
                decline_percent += parseFloat(t("#crm8_" + crm_id + "_0").html());
                goal += parseInt(t("#crm10_" + crm_id + "_0").html().split(' / ')[1]);
                count++;
            }
        });
        let c = goal > 0 && (100 * step1 / goal).toFixed(2);
        let d = step1 > 0 && (100 * step2 / step1).toFixed(2);
        count > 0 && (
            t(".all1").html(step1),
            t(".all2").html(step2),
            t(".all3").html(d),
            t(".all4").html(tablet),
            t(".all5").html((tablet_percent / count).toFixed(2)),
            t(".all6").html(prepaids),
            t(".all7").html((order_percent / count).toFixed(2)),
            t(".all8").html((decline_percent / count).toFixed(2)),
            t(".all9").html(c),
            t(".all10").html(step1 + " / " + goal));
    }

    function set_dates() {
        t("#from_date").prop("disabled", true);
        t("#to_date").prop("disabled", true);
        let cur_date = new Date;
        let formatted_date = format_date(cur_date.getFullYear(), cur_date.getMonth() + 1, cur_date.getDate());
        if ("date_today" == date_type) {
            from_date = formatted_date;
            to_date = formatted_date;
        }
        else if ("date_yesterday" == date_type) {
            cur_date.setDate(cur_date.getDate() - 1);
            from_date = format_date(cur_date.getFullYear(), cur_date.getMonth() + 1, cur_date.getDate());
            to_date = format_date(cur_date.getFullYear(), cur_date.getMonth() + 1, cur_date.getDate());
        }
        else if ("date_thisweek" == date_type) {
            let r = cur_date.getDate() + 1;
            0 == cur_date.getDay() ? r -= 7 : r -= cur_date.getDay();
            cur_date.setDate(r);
            from_date = format_date(cur_date.getFullYear(), cur_date.getMonth() + 1, cur_date.getDate());
            to_date = formatted_date;
        } else if ("date_thismonth" == date_type) {
            from_date = format_date(cur_date.getFullYear(), cur_date.getMonth() + 1, 1);
            to_date = formatted_date;
        }
        else if ("date_thisyear" == date_type) {
            from_date = format_date(cur_date.getFullYear(), 1, 1);
            to_date = formatted_date;
        }
        else if ("date_lastweek" == date_type) {
            let r = cur_date.getDate() + 1 - 7;
            0 == cur_date.getDay() ? r -= 7 : r -= cur_date.getDay();
            cur_date.setDate(r);
            from_date = format_date(cur_date.getFullYear(), cur_date.getMonth() + 1, cur_date.getDate());
            r = cur_date.getDate() + 6;
            cur_date.setDate(r);
            to_date = format_date(cur_date.getFullYear(), cur_date.getMonth() + 1, cur_date.getDate());
        } else if ("date_custom" == date_type) {
            from_date = "";
            to_date = "";
            t("#from_date").prop("disabled", false);
            t("#to_date").prop("disabled", false);
        }
        t("#from_date").val(from_date);
        t("#to_date").val(to_date);
    }

    function format_date(year, month, date) {
        if (month < 10) month = "0" + month;
        if (date < 10) date = "0" + date;
        return month + "/" + date + "/" + year;
    }

    function bulk_update_crm_goal(ids, goals) {
        show_waiting("sales", "", true);
        t.ajax({
            type: "GET",
            url: "/admin/ajax_setting_crm_goal",
            data: {
                crm_ids: ids,
                crm_goals: goals
            },
            success: function(result) {
                show_waiting("sales", "", false);
                if ("success" === result)
                    show_result();
            },
            failure: function() {
                show_waiting("sales", "", false);
                show_alert("sales", "Cannot update CRM Sales Goal.");
            }
        })
    }

    t(".input-daterange").datepicker({});
    t(".date_dropdown_menu li").on("click", function(e) {
        let a = t(this).text();
        date_type = t(this).find("a").attr("id");
        t(".date_toggle_button").html(a + ' <span class="caret"></span>');
        set_dates();
    });
    t(".sales_search_button").click(function() {
        show_result();
    });
    t(".btn_crm_position").click(function() {
        let e = "";
        let a = "";
        let r = 0;
        t(".crm_name_row").each(function(d) {
            let i = t(this).prop("id");
            let n = t(this).html();
            a += '<li style="margin-bottom: 10px"><span class="payment_badge payment_badge_grey">' + ++r + "</span></li>",
                "ll" == i.substring(0, 2) ? e += '<li id="' + i + '" class="position_row" style="cursor: move; margin-bottom: 10px"><span class="payment_badge payment_badge_blue">' + n + "</span></li>" : e += '<li id="' + i + '" class="position_row" style="cursor: move; margin-bottom: 10px"><span class="payment_badge payment_badge_red">' + n + "</span></li>"
        });
        t("#crm_number_ul").html(a);
        t("#crm_number_ul").disableSelection();
        t("#crm_position_ul").html(e);
        t("#crm_position_ul").sortable();
        t("#crm_position_ul").disableSelection();
        t("#crm_position_modal").modal("toggle");
    });
    t(".modal_btn_crm_position").click(function() {
        let changed_crm_positions = "";
        t(".position_row").each(function(e) {
            let r = t(this).prop("id");
            changed_crm_positions += ("" == changed_crm_positions ? "" : ",");
            changed_crm_positions += r;
        });
        show_waiting("sales", "", true);
        t.ajax({
            type: "GET",
            url: "/admin/ajax_crm_position_set",
            data: {
                crm_positions: changed_crm_positions
            },
            success: function(result) {
                show_waiting("sales", "", false);
                if ("OK" === result) {
                    crm_positions = changed_crm_positions;
                    show_result();
                }
            },
            failure: function() {
                show_waiting("sales", "", false);
                show_alert("sales", "Cannot save CRM positions.")
            }
        });
        t("#crm_position_modal").modal("toggle");
    });

    t(".btn_quick_edit").click(function() {
        let html = "";
        for (let i = 0; i < crm_list.length; i++) {
            html += '<div class="row" style="margin-bottom:5px;">';
            html += '<div class="col-xs-6 modal_input_label">' + crm_list[i]['crm_name'] + "</div>";
            html += '<div class="col-xs-6"><input type="text" id="editgoal_' + crm_list[i]['id'] + '" class="form-control input-sm edit_goals" value="' + crm_list[i]['sales_goal'] + '"></div>';
            html += "</div>";
        }
        t(".quick_edit_body").html(html);
    });
    t(".modal_btn_apply_goal").click(function() {
        let ids = "";
        let goals = "";
        t(".edit_goals").each(function() {
            "" !== ids && (ids += ",");
            "" !== goals && (goals += ",");
            ids += t(this).prop("id").substring(9);
            "" === t(this).val() ? goals += "0" : goals += t(this).val();
        });
        t("#quick_edit_modal").modal("toggle");
        bulk_update_crm_goal(ids, goals);
    });

    t(".table_dashboard").on("click", ".btn_setting", function() {
        selected_crm_id = parseInt(t(this).prop("id").substring(8));
        t.ajax({
            type: "GET",
            url: "/alert/ajax_setting_alert_list_by_cid",
            data: {
                crm_id: selected_crm_id
            },
            success: function(result) {
                alert_settings = result;
                let html = '<div class="row" style="margin-bottom:5px;">';
                html += '<div class="col-xs-6 modal_input_label"><label>Alert Level Management</label></div>';
                html += '</div>';
                if (result.length > 0) {
                    for (let i = 0; i < result.length; i++) {
                        result[i]['type__status'] && (html += '<div class="row" style="margin-bottom:5px;">',
                            html += '<div class="col-xs-6 modal_input_label">' + result[i]['type__alert_name'] + "</div>",
                            html += '<div class="col-xs-6"><input type="text" class="form-control input-sm edit_level_' + result[i]['type_id'] + '" value="' + result[i]['value1'] + '"></div>',
                            html += "</div>");
                    }
                    t(".modal_setting_alert_body").html(html);
                }
            },
            failure: function() {
                show_alert("setting", "Cannot load alert level information.")
            }
        });
        let crm = crm_list.filter(item => item['id'] === selected_crm_id)[0];
        t(".edit_crm_name").val(crm['crm_name']);
        t(".edit_crm_url").val(crm['crm_url']);
        t(".edit_crm_username").val(crm['username']);
        t(".edit_api_username").val(crm['api_username']);
        t(".edit_sales_goal").val(crm['sales_goal']);
        crm['paused'] ? t(".edit_crm_paused").prop("checked", true) : t(".edit_crm_paused").prop("checked", false);
    });
    t(".modal_btn_setting_edit").click(function() {
        if ("" === t(".edit_crm_name").val())
            return show_alert("setting", "Please input CRM Name."),
                void t(".edit_crm_name").focus();
        if ("" === t(".edit_crm_url").val())
            return show_alert("setting", "Please input CRM Site URL."),
                void t(".edit_crm_url").focus();
        if ("" === t(".edit_crm_username").val())
            return show_alert("setting", "Please input CRM User Name."),
                void t(".edit_crm_username").focus();
        if ("" === t(".edit_api_username").val())
            return show_alert("setting", "Please input API User Name."),
                void t(".edit_api_username").focus();
        if ("" === t(".edit_sales_goal").val())
            return show_alert("setting", "Please input Sales Goal."),
                void t(".edit_sales_goal").focus();
        for (let i = 0; i < alert_settings.length; i++) {
            if (alert_settings[i]['type__status'] && "" === t(".edit_level_" + alert_settings[i]['type_id']).val()) {
                return show_alert("setting", "Please input Alert level."),
                    void t(".edit_level_" + alert_settings[i]['type_id']).focus();
            }
        }
        t("#setting_edit_modal").modal("toggle");
        t.ajax({
            type: "GET",
            url: "/admin/ajax_setting_crm_edit",
            data: {
                crm_id: selected_crm_id,
                crm_name: t(".edit_crm_name").val(),
                crm_url: t(".edit_crm_url").val(),
                crm_username: t(".edit_crm_username").val(),
                api_username: t(".edit_api_username").val(),
                sales_goal: t(".edit_sales_goal").val(),
                crm_paused: t(".edit_crm_paused").prop("checked") ? 1 : 0
            },
            success: function(result) {
                if ('OK' === result)
                    show_result();
            },
            failure: function() {
                show_waiting("sales", "", false);
                show_alert("sales", "CRM information cannot be changed.");
            }
        });
        for (let i = 0; i < alert_settings.length; i++) {
            if (alert_settings[i]['type__status']) {
                t.ajax({
                    type: "GET",
                    url: "/alert/ajax_setting_alert_edit",
                    data: {
                        type_id: alert_settings[i]['type_id'],
                        crm_id: selected_crm_id,
                        value1: t(".edit_level_" + alert_settings[i]['type_id']).val(),
                        value2: 0
                    },
                    success: function(result) {

                    },
                    failure: function() {
                        show_alert("sales", "Alert level cannot be changed.")
                    }
                });
            }
        }
    });
    t(".dashboard_alert_body").on("click", ".btn_alert", function() {
        let a = t(this).prop("id").substring(6);
        -1 != t(this).html().indexOf("glyphicon-triangle-bottom") ? (t(this).html('<span class="glyphicon glyphicon-triangle-right" aria-hidden="true"></span>'),
            t("#abody_" + a).slideUp("1000", function() {
                t("#atitle_" + a).css("border-bottom", "1px solid #ebccd1"),
                    t("#atitle_" + a).css("background", "#f9f2f4"),
                    t("#abody_" + a).css("background", "#f9f2f4"),
                    t("#acontent_" + a).css("background", "#f9f2f4")
            })) : (t(this).html('<span class="glyphicon glyphicon-triangle-bottom" aria-hidden="true" style="color: #ffa5a5"></span>'),
            t("#abody_" + a).slideDown("1000"),
            t("#atitle_" + a).css("border-bottom", "none"),
            t("#atitle_" + a).css("background", "#fff"),
            t("#abody_" + a).css("background", "#fff"),
            t("#acontent_" + a).css("background", "#fff"))
    });

    setInterval(function () {
        // refresh();
        show_result();
    }, 5* 60 * 1000);

    crm_positions = t("#crm_positions").html();
    set_dates();

    // get dashboard_columns
    show_waiting("sales", "", true);
    t.ajax({
        type: "GET",
        url: "/admin/ajax_dashboard_columns_get",
        data: {},
        success: function(result) {
            show_waiting("sales", "", false);
            dashboard_columns = result;
            show_result();
        },
        failure: function() {
            show_waiting("sales", "", false);
            show_alert("sales", "Cannot load columns for dashboard.");
        }
    });
});
