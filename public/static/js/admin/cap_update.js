jQuery(document).ready(function(t) {
    function show_alert(content) {
        t(".cap_update_alert").html(content);
        t(".cap_update_alert").fadeIn(1000, function() {
            t(".cap_update_alert").fadeOut(3000)
        });
    }

    function show_edit_alert(content) {
        $(".affiliation_edit_alert").html(content);
        $(".affiliation_edit_alert").fadeIn(1e3, function () {
            $(".affiliation_edit_alert").fadeOut(3e3);
        });
    }

    function show_waiting(d) {
        d ? t(".cap_update_waiting").html(loading_gif) : t(".cap_update_waiting").html("");
    }

    function show_edit_waiting(status) {
        status ? $(".affiliate_edit_waiting").html(loading_gif) : $(".affiliate_edit_waiting").html("");
    }

    function format_date(year, month, date) {
        if (month < 10) month = "0" + month;
        if (date < 10) date = "0" + date;
        return month + "/" + date + "/" + year;
    }

    function format_time(hour, minute, second) {
        if (hour < 10) hour = "0" + hour;
        if (minute < 10) minute = "0" + minute;
        if (second < 10) second = "0" + second;
        return hour + ":" + minute + ":" + second;
    }

    function set_dates() {
        t("#from_date").prop("disabled", true);
        t("#to_date").prop("disabled", true);
        let date = new Date;
        let cur_date = new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
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
        }
        else if ("date_thismonth" == date_type) {
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
        }
        else if ("date_custom" == date_type) {
            from_date = "";
            to_date = "";
            t("#from_date").prop("disabled", false);
            t("#to_date").prop("disabled", false);
        }
        t("#from_date").val(from_date);
        t("#to_date").val(to_date);
    }

    function get_cap_update_list() {
        show_waiting(true);
        t.ajax({
            type: "GET",
            url: "/admin/ajax_crm_list",
            data: {},
            success: function(response) {
                show_waiting(false);
                let crm_list = response;
                if ("" == t("#from_date").val()) {
                    show_alert("Please select FROM DATE.")
                }
                else if ("" == t("#to_date").val()) {
                    show_alert("Please select TO DATE.")
                }
                else {
                    show_waiting(true);
                    t.ajax({
                        type: "GET",
                        url: "/admin/ajax_cap_update_list/",
                        data: {},
                        success: function(response) {
                            show_waiting(false);
                            cap_update_list = response;

                            let html = "";

                            let affiliate_goal_id = -1;
                            for (let i = 0; i < cap_update_list.length; i++) {
                                let affiliate_goal = cap_update_list[i];
                                if (affiliate_goal_id !== affiliate_goal['affiliate_id']) {
                                    if (-1 !== affiliate_goal_id)
                                        html += '</div></div></div>';
                                    affiliate_goal_id = affiliate_goal['affiliate_id'];

                                    html += '<div class="col-lg-4 col-md-6 col-sm-12 col-xs-12 c_item"><div>';
                                    html += '<button type="button" class="btn btn-link btn-sm btn_affiliation_edit payment_badge_blue" id="aedit_' + affiliate_goal['affiliate_id'] + '" data-toggle="modal" data-target="#affiliation_edit_modal" style="font-size: 18px; font-weight: bold; padding-left: 0;">' + affiliate_goal['affiliate_name'] + '</button>';
                                    if (null == affiliate_goal['afid'])
                                        html += '<p>AFIDS:</p>';
                                    else
                                        html += '<p>AFIDS: ' + affiliate_goal['afid'] + '</p>';

                                    html += '<h4 style="color: #6772e5">Sales Progress</h4>';
                                    html += '<div class="row c_cnt_header">';
                                    html += '<div style="color: #6772e5" class="col-lg-4 col-md-4 col-sm-4 col-xs-4">OFFER</div>';
                                    html += '<div style="color: #6772e5" class="col-lg-3 col-md-3 col-sm-3 col-xs-3">PROGRESS</div>';
                                    html += '<div style="color: #6772e5" class="col-lg-5 col-md-5 col-sm-5 col-xs-5">LAST UPDATED</div>';
                                    html += '</div>';
                                    html += '<div class="c_cnt_list">';
                                }
                                html += '<div class="row">';
                                html += '<div class="col-lg-4 col-md-4 col-sm-4 col-xs-4">' + affiliate_goal['offer_name'] + '</div>';
                                html += '<div class="col-lg-3 col-md-3 col-sm-3 col-xs-3" id="capgoal_' + affiliate_goal['affiliate_id'] + '_' + affiliate_goal['offer_id'] + '">[0/' + affiliate_goal['goal'] + ']</div>';
                                html += '<div class="col-lg-5 col-md-5 col-sm-5 col-xs-5" id="updated_' + affiliate_goal['affiliate_id'] + '_' + affiliate_goal['offer_id'] + '"></div>';
                                html += '</div>';
                            }
                            t(".div_cap_update_body").html(html);

                            for (let j = 0; j < crm_list.length; j++)
                                get_cap_update_goal_list(crm_list[j]['id']);
                        },
                        failure: function(t) {
                            show_waiting(false);
                            show_alert("Cannot load Affiliate Sales Goal information.")
                        }
                    });
                }
            },
            failure: function() {
                show_waiting(false);
                show_alert("Cannot load CRM site information.");
            }
        });
    }

    function get_cap_update_goal_list(crm_id) {
        t.ajax({
            type: "GET",
            url: "/admin/api/cap_update_result",
            data: {
                crm_id: crm_id,
                from_date: t("#from_date").val(),
                to_date: t("#to_date").val()
            },
            success: function(response) {
                let goal = response;

                if (goal.length === 0)
                    return;

                goal = goal[0];
                goals.push(goal);
                for (let i = 0; i < cap_update_list.length; i++) {
                    let affiliate_goal = cap_update_list[i];
                    if (goal['crm'] === affiliate_goal['crm_id']) {
                        let count = 0;
                        let afids = affiliate_goal['afid'].split(',');
                        let campaign_ids = affiliate_goal['step1'];
                        let goal_data = jQuery.parseJSON(goal['result'].replace(new RegExp("'", 'g'), '"'));
                        for (let k = 0; k < goal_data.length; k++) {
                            let campaign_prospects = goal_data[k];
                            for (let l = 0; l < campaign_ids.length; l++) {
                                if (campaign_ids[l] === campaign_prospects[0]) {
                                    for (let m = 0; m < campaign_prospects[1].length; m++) {
                                        for (let n = 0; n < afids.length; n++) {
                                            if (campaign_prospects[1][m]['id'] === afids[n].split('(')[0]) {
                                                count += campaign_prospects[1][m]['initial_customers'];
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        $("#capgoal_" + affiliate_goal['affiliate_id'] + '_' + affiliate_goal['offer_id']).html(
                            '[' + count.toString() + '/' + affiliate_goal['goal'] + ']'
                        );

                        let est = new Date(goal['updated_at'].slice(0, 19).replace('T', ' '));
                        est.setHours(est.getHours() - 4);
                        $("#updated_" + affiliate_goal['affiliate_id'] + '_' + affiliate_goal['offer_id']).html(
                            format_date(est.getFullYear(), est.getMonth() + 1, est.getDate()) + ' ' +
                            format_time(est.getHours(), est.getMinutes(), est.getSeconds())
                        );
                    }
                }
            },
            failure: function() {
                show_waiting(false);
                show_alert("Cannot load sales information.");
            }
        });
    }

    function get_export_result() {
        let affiliate_goal_id = -1;
        let text_result = '';
        for (let i = 0; i < cap_update_list.length; i++) {
            let affiliate_goal = cap_update_list[i];
            if (affiliate_goal_id !== affiliate_goal['affiliate_id']) {
                affiliate_goal_id = affiliate_goal['affiliate_id'];
                if (i !== 0) text_result += '\n\n';
                text_result += "To " + affiliate_goal['affiliate_name'] + '\n\n';
                text_result += "Here are remaining caps for the week\n\n";
            }
            for (let j = 0; j < goals.length; j++) {
                let goal = goals[j];
                if (goal['crm'] === affiliate_goal['crm_id']) {
                    let count = 0;
                    let afids = affiliate_goal['afid'].split(',');
                    let campaign_ids = affiliate_goal['step1'];
                    let goal_data = jQuery.parseJSON(goal['result'].replace(new RegExp("'", 'g'), '"'));
                    for (let k = 0; k < goal_data.length; k++) {
                        let campaign_prospects = goal_data[k];
                        for (let l = 0; l < campaign_ids.length; l++) {
                            if (campaign_ids[l] === campaign_prospects[0]) {
                                for (let m = 0; m < campaign_prospects[1].length; m++) {
                                    for (let n = 0; n < afids.length; n++) {
                                        if (campaign_prospects[1][m]['id'] === afids[n].split('(')[0]) {
                                            count += campaign_prospects[1][m]['initial_customers'];
                                        }
                                    }
                                }
                            }
                        }
                    }
                    text_result += affiliate_goal['offer_name'] + ' ';
                    text_result += (affiliate_goal['goal'] - count).toString() + ' remaining ';
                    text_result += '(' + affiliate_goal['goal'] + ' for the week)\n';
                }
            }
        }
        let data = new Blob([text_result], {type: 'text/plain'});
        let textFile = window.URL.createObjectURL(data);
        let link = document.getElementById('downloadlink');
        link.setAttribute('download', 'cap_result_' +
            t("#from_date").val().replace(new RegExp('/', 'g'), '-') + '_' +
            t("#to_date").val().replace(new RegExp('/', 'g'), '-') + '.txt');
        link.href = textFile;
    }

    t(".input-daterange").datepicker({});
    t(".date_dropdown_menu li").on("click", function(e) {
        let r = t(this).text();
        date_type = t(this).find("a").attr("id");
        t(".date_toggle_button").html(r + ' <span class="caret"></span>');
        set_dates();
    });
    t(".cap_search_button").click(function() {
        get_cap_update_list();
    });
    t(".btn_cap_export").click(function() {
        get_export_result();
    });


    let loading_gif = '<img src="/static/images/loading.gif" style="width: 22px; height: 22px;">';
    let from_date = "";
    let to_date = "";
    let cap_update_list = null;
    let goals = [];
    let date_type = "date_thisweek";

    set_dates();
    get_cap_update_list();

    let offers = null;
    let affiliations = null;
    let selected_affiliate_id = -1;
    get_offer_list();
    get_affiliation_list();
    function get_offer_list() {
        show_waiting(true);
        t.ajax({
            type: "GET",
            url: "/admin/api/offer",
            data: {},
            success: function (response) {
                show_waiting(false);
                offers = response;
            },
            failure: function () {
                show_waiting(false);
                show_alert("Offers cannot be loaded.");
            }
        })
    }
    function get_affiliation_list() {
        show_waiting(true);
        $(".table_affiliation_body").html("");
        t.ajax({
            type: "GET",
            url: "/admin/ajax_affiliation_list",
            data: {},
            success: function (response) {
                show_waiting(false);
                affiliations = response;
            },
            failure: function () {
                show_waiting(false);
                show_alert("Cannot load affiliate goal information.");
            }
        })
    }
    function edit_affiliate(offer_ids, offer_goals, s1_payouts, s2_ids, s2_payouts) {
        show_waiting("main", true);
        $.ajax({
            type: "GET",
            url: "/admin/ajax_edit_affiliate",
            data: {
                affiliate_id: selected_affiliate_id,
                name: $(".edit_affiliation_name").val(),
                afid: $(".edit_affiliation_afid").val(),
                offer_ids: offer_ids,
                offer_goals: offer_goals,
                s1_payouts: s1_payouts,
                s2_ids: s2_ids,
                s2_payouts: s2_payouts
            },
            success: function (response) {
                show_waiting("main", false);
                if ("OK" === response) {
                    get_affiliation_list();
                    get_cap_update_list();
                }
            },
            failure: function () {
                show_waiting("main", false);
                show_alert("main", "Affiliate cannot be changed.");
            }
        });
    }
    function delete_affiliate() {
        show_waiting("main", true);
        $.ajax({
            type: "GET",
            url: "/admin/ajax_delete_affiliate",
            data: {
                affiliate_id: selected_affiliate_id
            },
            success: function (response) {
                show_waiting("main", false);
                if ("OK" === response) {
                    get_affiliation_list();
                    get_cap_update_list();
                }
            },
            failure: function () {
                show_waiting("main", false);
                show_alert("main", "Affiliate cannot be deleted.");
            }
        });
    }
    function make_html(affiliate_offers) {
        let html = '<table id="id_affiliation_offer_caps_table" class="table table-hover"' + (0 === affiliate_offers.length ? ' style="display:none"' : "") + '>';
        html += '<thead id="id_affiliation_offer_caps_header"><tr>' +
            '<th>Offer Name</th>' +
            '<th>Offer Cap</th>' +
            '<th>Step1 CPA</th>';
        for (let i = 0; i < affiliate_offers.length; i++) {
            let offer = affiliate_offers[i];
            let offer_type = offers.filter(item => item['id'] === offer['offer_id'])[0]['type'];
            if (2 === offer_type) {
                html += '<th>Step2 CPA</th>';
                break;
            }
        }
        html += '</tr></thead>';
        html += '<tbody id="id_affiliation_offer_caps_body">';

        for (let i = 0; i < affiliate_offers.length; i++) {
            let offer = affiliate_offers[i];
            let offer_full = offers.filter(item => item['id'] === offer['offer_id'])[0];
            html += '<tr>';
            html += '<td>' + offer['offer_name'] + '</td>';
            html += '<td><input type="text" id="editgoal_' + offer['offer_id'] + '" class="form-control input-sm edit_goals" value="' + offer['affiliate_offer_goal'] + '"></td>';
            html += '<td><input type="text" id="s1payout_' + offer['offer_id'] + '" class="form-control input-sm s1_edit_payouts" value="' + (null == offer['affiliate_offer_s1_payout'] || 0 === offer['affiliate_offer_s1_payout'] ? "": offer['affiliate_offer_s1_payout']) + '" placeholder="' + offer_full['s1_payout'] + '"/></td>';
            if (2 === offer_full['type'])
                html += '<td><input type="text" id="s2payout_' + offer['offer_id'] + '" class="form-control input-sm s2_edit_payouts" value="' + (null == offer['affiliate_offer_s2_payout'] || 0 === offer['affiliate_offer_s2_payout'] ? "": offer['affiliate_offer_s2_payout']) + '" placeholder="' + offer_full['s2_payout'] + '"/></td>';
            html += '</tr>';
        }
        html += '</tbody></table>';
        return html;
    }
    function check_afids(afids) {
        afids = afids.split(',');
        if ((new Set(afids)).size !== afids.length)
            return false;
        // for (let i = 0; i < afids.length; i++) {
        //     if (isNaN(afids[i]))
        //         return false;
        // }
        return true;
    }

    $(document).on("click", ".btn_affiliation_edit", function () {
        selected_affiliate_id = parseInt($(this).prop("id").substring(6));
        let affiliate = affiliations.filter(item => item['affiliate_id'] === selected_affiliate_id)[0];

        let offer_ids = affiliate['sub_result'].map(item => item['offer_id']);
        let all_options = '';
        let chosen_options = '';
        for (let i = 0; i < offers.length; i++) {
            if (offer_ids.includes(offers[i]['id']))
                chosen_options += '<option value=' + offers[i]['id'] + '>' + offers[i]['name'] + '</option>';
            else
                all_options += '<option value=' + offers[i]['id'] + '>' + offers[i]['name'] + '</option>';
        }
        $(".all_options").html(all_options);
        $(".chosen_options").html(chosen_options);

        $(".edit_affiliation_name").val(affiliate['affiliate_name']);
        $(".edit_affiliation_afid").val(affiliate['affiliate_afid']);
        $("#edit_special_code").val(affiliate['affiliate_code']);

        $(".affiliation_offer_caps").html(make_html(affiliate['sub_result']));
    });
    $(".modal_btn_affiliation_edit").click(function () {
        if ("" === $(".edit_affiliation_name").val()) {
            show_edit_alert("edit", "Please input Affiliate Name.");
            $(".edit_affiliation_name").focus();
            return;
        }
        if ("" === $(".edit_affiliation_afid").val()) {
            show_edit_alert("edit", "Please input AFIDs of Affiliate.");
            $(".edit_affiliation_afid").focus();
            return;
        }
        if (false === check_afids($(".edit_affiliation_afid").val())) {
            show_edit_alert("edit", "There is duplicates or incorrect ids in AFIDs. Please check again.");
            $(".edit_affiliation_afid").focus();
            return;
        }

        $("#affiliation_edit_modal").modal("toggle");
        let ids = [];
        let goals = [];
        let s1_payouts = [];
        let s2_ids = [];
        let s2_payouts = [];
        $(".edit_goals").each(function () {
            ids.push($(this).prop("id").substring(9));
            goals.push("" == $(this).val() ? "0" : $(this).val());
        });
        $(".s1_edit_payouts").each(function () {
            s1_payouts.push("" == $(this).val() ? "0" : $(this).val());
        });
        $(".s2_edit_payouts").each(function () {
            s2_ids.push($(this).prop("id").substring(9));
            s2_payouts.push("" == $(this).val() ? "0" : $(this).val());
        });

        edit_affiliate(ids.join(','), goals.join(','), s1_payouts.join(','), s2_ids.join(','), s2_payouts.join(','));
    });
    $(".modal_btn_affiliation_delete").click(function () {
        $("#affiliation_delete_modal").modal("toggle");
        $("#affiliation_edit_modal").modal("toggle");
        delete_affiliate();
    });

    function refresh_table() {
        let chosen_options = $('.chosen_options option');

        if (chosen_options.length > 0)
            $("#id_affiliation_offer_caps_table").css("display", "table");
        else
            $("#id_affiliation_offer_caps_table").css("display", "none");

        let html = '<tr>' +
            '<th>Offer Name</th>' +
            '<th>Offer Cap</th>' +
            '<th>Step1 CPA</th>';
        for (let i = 0; i < chosen_options.length; i++) {
            let offer = offers.filter(item => item['id'] === chosen_options[i].value)[0];
            if (2 === offer['type']) {
                html += '<th>Step2 CPA</th>';
                break;
            }
        }
        html += '</tr>';
        $("#id_affiliation_offer_caps_header").html(html);
    }
    $('.go_in').click(function() {
        let selected_options = $('.all_options option:selected');
        selected_options.remove().appendTo('.chosen_options');

        let body = document.getElementById('id_affiliation_offer_caps_body');

        for (let i = 0; i < selected_options.length; i++) {
            let offer = offers.filter(item => item['id'] == selected_options[i].value)[0];
            let new_offer = document.createElement('tr');
            let html = '<tr>';
            html += '<td>' + offer['name'] + '</td>';
            html += '<td><input type="text" id="editgoal_' + offer['id'] + '" class="form-control input-sm edit_goals" value=""></td>';
            html += '<td><input type="text" id="s1payout_' + offer['id'] + '" class="form-control input-sm s1_edit_payouts" value="" placeholder="' + offer['s1_payout'] + '"/></td>';
            if (2 === offer['type']) {
                html += '<td><input type="text" id="s2payout_' + offer['id'] + '" class="form-control input-sm s2_edit_payouts" value="" placeholder="' + offer['s2_payout'] + '"/></td>';
            }
            html += '</tr>';
            new_offer.innerHTML = html;
            body.appendChild(new_offer);
        }
        refresh_table();
    });
    $('.go_out').click(function() {
        let selected_options = $('.chosen_options option:selected');
        selected_options.remove().appendTo('.all_options');

        for (let i = 0; i < selected_options.length; i++) {
            $("#editgoal_" + selected_options[i].value).parent().parent().remove();
        }
        refresh_table();
    });
});
