jQuery(document).ready(function(t) {
    function show_alert(content) {
        t(".billing_alert").html(content);
        t(".billing_alert").fadeIn(1000, function() {
            t(".billing_alert").fadeOut(3000)
        });
    }

    function show_edit_alert(content) {
        $(".affiliation_edit_alert").html(content);
        $(".affiliation_edit_alert").fadeIn(1e3, function () {
            $(".affiliation_edit_alert").fadeOut(3e3);
        });
    }

    function show_waiting(d) {
        d ? t(".billing_waiting").html(loading_gif) : t(".billing_waiting").html("");
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
        var date = new Date;
        var cur_date = new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
        var formatted_date = format_date(cur_date.getFullYear(), cur_date.getMonth() + 1, cur_date.getDate());
        if ("date_thisweek" == date_type) {
            var r = cur_date.getDate() + 1;
            0 == cur_date.getDay() ? r -= 7 : r -= cur_date.getDay();
            cur_date.setDate(r);
            from_date = format_date(cur_date.getFullYear(), cur_date.getMonth() + 1, cur_date.getDate());
            to_date = formatted_date;
        }
        else if ("date_lastweek" == date_type) {
            r = cur_date.getDate() + 1 - 7;
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
        else {
            let date_selected = date_type.split('_')[1];
            from_date = date_selected.split('-')[0];
            to_date = date_selected.split('-')[1];
            from_date = from_date.substring(0, 2) + '/' + from_date.substring(3, 5) + '/20' + from_date.substring(6);
            to_date = to_date.substring(0, 2) + '/' + to_date.substring(3, 5) + '/20' + to_date.substring(6);
        }
        t("#from_date").val(from_date);
        t("#to_date").val(to_date);
    }

    function get_billing_list() {
        if ("" === t("#from_date").val()) {
            show_alert("Please select FROM DATE.")
        }
        else if ("" === t("#to_date").val()) {
            show_alert("Please select TO DATE.")
        }
        else {
            show_waiting(true);
            t.ajax({
                type: "GET",
                url: "../daemon/ajax_admin/crm_list.php",
                data: {},
                success: function (e) {
                    show_waiting(false);
                    if ("error" == e) {
                        show_alert("Cannot load CRM site information.");
                    }
                    else if ("no_cookie" == e) {
                        window.location.href = "../../admin/login.php";
                    }
                    else {
                        var crm_list = jQuery.parseJSON(e);
                        show_waiting(true);
                        t.ajax({
                            type: "GET",
                            url: "../daemon/ajax_admin/billing_list.php",
                            data: {
                                date_type: date_type,
                                from_date: t("#from_date").val(),
                                to_date: t("#to_date").val()
                            },
                            success: function(e) {
                                show_waiting(false);
                                if ("no_cookie" === e)
                                    return void (window.location.href = "../../admin/login.php");

                                billing_list = jQuery.parseJSON(e);

                                if (0 === billing_list.length) {
                                    show_alert("There is no billing data.");
                                    return;
                                }

                                let html = "";

                                let affiliate_id = -1;
                                for (let i = 0; i < billing_list.length; i++) {
                                    let billing = billing_list[i];
                                    // ["6", "2", "3", "200", "Full Zoom Media", "12,58", "Vital X", "Falcor CRM", "2500"]
                                    if (affiliate_id !== billing['affiliate_id']) {
                                        if (-1 !== affiliate_id)
                                            html += '</div></div></div>';
                                        affiliate_id = billing['affiliate_id'];

                                        html += '<div class="col-lg-4 col-md-6 col-sm-12 col-xs-12 c_item"><div>';
                                        html += '<button type="button" class="btn btn-link btn-sm btn_affiliation_edit payment_badge_blue" id="aedit_' + billing['affiliate_id'] + '" data-toggle="modal" data-target="#affiliation_edit_modal" style="font-size: 18px; font-weight: bold; padding-left: 0;">' + billing['affiliate_name'] + '</button>';
                                        if (null == billing['afid'])
                                            html += '<p>AFIDS:</p>';
                                        else
                                            html += '<p>AFIDS: ' + billing['afid'] + '</p>';
                                        html += '<p style="margin-top: 5px;" id="tti_' + billing['affiliate_id'] + '">Total To Invoice: $ 0.00</p>';

                                        html += '<h4 style="color: #6772e5">Sales Progress</h4>';
                                        html += '<div class="row c_cnt_header">';
                                        html += '<div style="color: #6772e5; text-align: center;" class="col-lg-4 col-md-4 col-sm-4 col-xs-4">OFFER</div>';
                                        html += '<div style="color: #6772e5" class="col-lg-2 col-md-2 col-sm-2 col-xs-2">SALES</div>';
                                        html += '<div style="color: #6772e5" class="col-lg-3 col-md-3 col-sm-3 col-xs-3">CPA</div>';
                                        html += '<div style="color: #6772e5" class="col-lg-3 col-md-3 col-sm-3 col-xs-3">TOTAL</div>';
                                        html += '</div>';
                                        html += '<div class="c_cnt_list" id="cnt_list_' + billing['affiliate_id'] + '">';
                                    }
                                    html += '<div class="row">';
                                    html += '<div style="text-align: center" class="col-lg-4 col-md-4 col-sm-4 col-xs-4">' + billing['offer_name'] + '</div>';
                                    html += '<div style="text-align: center" class="col-lg-2 col-md-2 col-sm-2 col-xs-2" id="capgoal_' + billing['affiliate_id'] + '_' + billing['offer_id'] + '"></div>';
                                    if (null == billing['s1_payout'] || 0 == billing['s1_payout'])
                                        html += '<div class="col-lg-3 col-md-3 col-sm-3 col-xs-3" id="cpa_' + billing['affiliate_id'] + '_' + billing['offer_id'] + '">$ ' + billing['s1_payout_'] + '.00</div>';
                                    else
                                        html += '<div class="col-lg-3 col-md-3 col-sm-3 col-xs-3" id="cpa_' + billing['affiliate_id'] + '_' + billing['offer_id'] + '"><b>$ ' + billing['s1_payout'] + '.00</b></div>';
                                    html += '<div class="col-lg-3 col-md-3 col-sm-3 col-xs-3" id="total_' + billing['affiliate_id'] + '_' + billing['offer_id'] + '"></div>';
                                    html += '</div>';
                                }
                                t(".div_billing_body").html(html);

                                if (billing_list.length > 0) {
                                    for (let i = 0; i < crm_list.length; i++) {
                                        get_billing_goal_list(crm_list[i][0]);
                                    }
                                }
                            },
                            failure: function() {
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
    }

    function get_billing_goal_list(crm_id) {
        t.ajax({
            type: "GET",
            url: "../daemon/ajax_admin/billing_goal_list.php",
            data: {
                crm_id: crm_id,
                from_date: t("#from_date").val(),
                to_date: t("#to_date").val()
            },
            success: function(e) {
                let goal = jQuery.parseJSON(e);

                if (goal[0] === 'error') {
                    show_alert('Cannot load sales information of ' + goal[1]);
                }
                else if (goal[0] === 'no_cookie') {
                    window.location.href = '../../admin/login.php';
                }
                else {
                    for (let i = 0; i < billing_list.length; i++) {
                        let billing = billing_list[i];
                        if (goal[1] == billing['crm_id']) {
                            let count = 0;
                            let afids = billing['afid'].split(',');
                            let campaign_ids = billing['campaign_ids'].split(',');

                            let specials = {};

                            for (let k = 0; k < goal[2].length; k++) {
                                let campaign_prospects = goal[2][k];
                                for (let l = 0; l < campaign_ids.length; l++) {
                                    if ("step1" === campaign_ids[l].split('_')[0]) {
                                        let campaign_id = campaign_ids[l].split('_')[1];
                                        if (campaign_id == campaign_prospects[0]) {
                                            for (let m = 0; m < campaign_prospects[1].length; m++) {
                                                for (let n = 0; n < afids.length; n++) {
                                                    if (campaign_prospects[1][m][0] == afids[n].split('(')[0]) {
                                                        if (afids[n].split('(').length == 2) {
                                                            let special_id = afids[n];
                                                            special_id = afids[n].split('(')[0];
                                                            let special_price = afids[n].split('(')[1];
                                                            special_price = special_price.substr(0, special_price.length - 1);

                                                            if (special_id in specials)
                                                                specials[special_id] = [special_price, specials[special_id][1] + parseInt(campaign_prospects[1][m][2])];
                                                            else
                                                                specials[special_id] = [special_price, parseInt(campaign_prospects[1][m][2])];
                                                        }
                                                        else {
                                                            count += campaign_prospects[1][m][2];
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            billing['sales'] = count;
                            $("#capgoal_" + billing['affiliate_id'] + '_' + billing['offer_id']).html(count ? count.toString() : '');
                            let price = 0;
                            if (null == billing['s1_payout'] || 0 == billing['s1_payout'])
                                price = billing['s1_payout_'];
                            else
                                price = billing['s1_payout'];
                            $("#total_" + billing['affiliate_id'] + '_' + billing['offer_id']).html(
                                '$ ' + (count ? ((count * price).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')) : '-')
                            );

                            let tti = parseFloat($("#tti_" + billing['affiliate_id']).html().substring(20).replace(',', ''));
                            tti += parseFloat(count * price);

                            if (!$.isEmptyObject(specials)) {
                                for (let key in specials) {
                                    console.log(key, specials[key]);
                                    let html = '<div class="row">';
                                    html += '<div style="text-align: center" class="col-lg-4 col-md-4 col-sm-4 col-xs-4">' + billing['offer_name'] + ' - ID ' + key + '</div>';
                                    html += '<div style="text-align: center" class="col-lg-2 col-md-2 col-sm-2 col-xs-2" id="capgoal_' + billing['affiliate_id'] + '_' + billing['offer_id'] + '">' + specials[key][1] + '</div>';
                                    html += '<div class="col-lg-3 col-md-3 col-sm-3 col-xs-3" id="cpa_' + billing['affiliate_id'] + '_' + billing['offer_id'] + '">$ ' + specials[key][0] + '.00</div>';
                                    html += '<div class="col-lg-3 col-md-3 col-sm-3 col-xs-3" id="total_' + billing['affiliate_id'] + '_' + billing['offer_id'] + '">$ ' + ((specials[key][0] * specials[key][1]).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')) + '</div>';
                                    html += '</div>';

                                    tti += parseFloat(specials[key][0] * specials[key][1]);
                                    $('#cnt_list_' + billing['affiliate_id']).append(html);
                                }
                            }

                            $("#tti_" + billing['affiliate_id']).html('Total To Invoice: $ ' + tti.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,'));
                        }
                    }
                }
            },
            failure: function() {
                show_waiting(false);
                show_alert("Cannot load sales information.");
            }
        });
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async function get_export_result() {
        let affiliate_id = -1;
        let result;
        for (let i = 0; i < billing_list.length; i++) {
            let billing = billing_list[i];
            if (affiliate_id !== billing['affiliate_id']) {
                if (0 !== i) {
                    result['tti'] = '$ ' + (result['tti'].toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,'));
                    window.location.href = "./export_billing.php?from_date=" + t("#from_date").val() + "&to_date=" + t("#to_date").val() + "&data=" + JSON.stringify(result);
                    await sleep(2000);
                }
                result = {};
                result['affiliate_name'] = billing['affiliate_name'];
                result['afid'] = billing['afid'];
                result['weekof'] = t("#from_date").val() + '-' + t("#to_date").val();
                result['tti'] = 0;
                result['offers'] = [];
                affiliate_id = billing['affiliate_id'];
            }

            let cpa = 0;
            if (null == billing['s1_payout'] || 0 == billing['s1_payout'])
                cpa = billing['s1_payout_'];
            else
                cpa = billing['s1_payout'];
            result['offers'].push({
                'offer': billing['offer_name'],
                'sales': billing['sales'],
                'cpa': '$ ' + cpa + '.00',
                'total': '$ ' + (billing['sales'] ? ((billing['sales'] * cpa).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')) : '-'),
            });

            result['tti'] += parseFloat(billing['sales'] * cpa);
        }
        result['tti'] = '$ ' + (result['tti'].toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,'));
        await sleep(1000);
        window.location.href = "./export_billing.php?from_date=" + t("#from_date").val() + "&to_date=" + t("#to_date").val() + "&data=" + JSON.stringify(result);
    }

    t(".input-daterange").datepicker({});
    t(".date_dropdown_menu li").on("click", function(e) {
        let r = t(this).text();
        date_type = t(this).find("a").attr("id");
        t(".date_toggle_button").html(r + ' <span class="caret"></span>');
        set_dates();
    });
    t(".cap_search_button").click(function() {
        get_billing_list();
    });
    t(".btn_billing_export").click(function() {
        let result = get_export_result();
    });


    let loading_gif = '<img src="../images/loading.gif" style="width:22px;height:22px;">';
    let from_date = "";
    let to_date = "";
    let billing_list = null;
    let date_type = "date_thisweek";

    set_dates();
    get_billing_list();


    let offers = null;
    let affiliations = null;
    let selected_affiliate_id = -1;
    get_offer_list();
    get_affiliation_list();
    function get_offer_list() {
        show_waiting(true);
        t.ajax({
            type: "GET",
            url: "../daemon/ajax_admin/offer_list.php",
            data: {},
            success: function (e) {
                show_waiting(false);
                if ("no_cookie" === e)
                    window.location.href = "../../admin/login.php";
                else if ("error" === e) {
                    show_alert("Offers cannot be loaded.");
                }
                else {
                    offers = jQuery.parseJSON(e);
                }
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
            url: "../daemon/ajax_admin/setting_affiliation_list.php",
            data: {},
            success: function (e) {
                show_waiting(false);
                if ("no_cookie" === e)
                    return void (window.location.href = "../../admin/login.php");

                affiliations = jQuery.parseJSON(e);
            },
            failure: function () {
                show_waiting(false);
                show_alert("Cannot load affiliate goal information.");
            }
        })
    }
    function get_affiliate_offers() {
        show_edit_waiting(true);
        $.ajax({
            type: "GET",
            url: "../daemon/ajax_admin/setting_affiliation_offer_list.php",
            data: {
                affiliate_id: selected_affiliate_id
            },
            success: function (data) {
                show_edit_waiting(false);
                if ("error" == data)
                    show_edit_alert("Affiliate offers cannot be loaded.");
                else if ("no_cookie" == data)
                    window.location.href = "../../admin/login.php";
                else {
                    let selected_offers = jQuery.parseJSON(data);
                    let all_options = '';
                    let chosen_options = '';
                    for (let i = 0; i < offers.length; i++) {
                        if (selected_offers.includes(offers[i][0]))
                            chosen_options += '<option value="' + offers[i][0] + '">' + offers[i][1] + '</option>';
                        else
                            all_options += '<option value="' + offers[i][0] + '">' + offers[i][1] + '</option>';
                    }
                    $(".all_options").html(all_options);
                    $(".chosen_options").html(chosen_options);
                }
            },
            failure: function () {
                show_edit_waiting(false);
                show_edit_alert("Affiliate offers cannot be loaded.");
            }
        });
    }
    function edit_affiliate(offer_ids, offer_goals, s1_payouts, s2_ids, s2_payouts) {
        show_waiting("main", true);
        $.ajax({
            type: "GET",
            url: "../daemon/ajax_admin/setting_affiliation_edit.php",
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
            success: function (status) {
                show_waiting("main", false);
                if ("error" == status)
                    show_alert("main", "Affiliate cannot be changed.");
                else if ("no_cookie" == status)
                    window.location.href = "../../admin/login.php";
                else if ("success" == status) {
                    get_affiliation_list();
                    get_billing_list();
                }
            },
            failure: function () {
                show_waiting("main", false);
                show_alert("main", "Affiliate cannot be changed.");
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
            let offer_type = offers.filter(item => item[0] == offer[2])[0][5];
            if (2 == offer_type) {
                html += '<th>Step2 CPA</th>';
                break;
            }
        }
        html += '</tr></thead>';
        html += '<tbody id="id_affiliation_offer_caps_body">';

        for (let i = 0; i < affiliate_offers.length; i++) {
            let offer = affiliate_offers[i];
            let offer_type = offers.filter(item => item[0] == offer[2])[0];
            html += '<tr>';
            html += '<td>' + offer[3] + '</td>';
            html += '<td><input type="text" id="editgoal_' + offer[2] + '" class="form-control input-sm edit_goals" value="' + offer[1] + '"></td>';
            html += '<td><input type="text" id="s1payout_' + offer[2] + '" class="form-control input-sm s1_edit_payouts" value="' + (null == offer[7] || 0 == offer[7] ? "": offer[7]) + '" placeholder="' + offer_type[6] + '"/></td>';
            if (2 == offer_type[5])
                html += '<td><input type="text" id="s2payout_' + offer[2] + '" class="form-control input-sm s2_edit_payouts" value="' + (null == offer[8] || 0 == offer[8] ? "": offer[8]) + '" placeholder="' + offer_type[7] + '"/></td>';
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
        let all_options = "";
        for (let i = 0; i < offers.length; i++) {
            all_options += '<option value="' + offers[i][0] + '">' + offers[i][1] + '</option>';
        }
        $(".all_options").html(all_options);
        $(".chosen_options").html("");
        $(".affiliation_offer_caps").html("");

        selected_affiliate_id = $(this).prop("id").substring(6);
        let affiliate = affiliations.filter(item => item[0][0] === selected_affiliate_id)[0];
        $(".edit_affiliation_name").val(affiliate[0][1]);
        $(".edit_affiliation_afid").val(affiliate[0][2]);

        $(".affiliation_offer_caps").html(make_html(affiliate[1]));

        get_affiliate_offers();
    });
    $(".modal_btn_affiliation_edit").click(function () {
        if ("" == $(".edit_affiliation_name").val()) {
            show_edit_alert("edit", "Please input Affiliate Name.");
            $(".edit_affiliation_name").focus();
            return;
        }
        if ("" == $(".edit_affiliation_afid").val()) {
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
            let offer = offers.filter(item => item[0] === chosen_options[i].value)[0];
            if (2 == offer[5]) {
                html += '<th>Step2 CPA</th>';
                break;
            }
        }
        html += '</tr>';
        $("#id_" + add + "affiliation_offer_caps_header").html(html);
    }
    $('.go_in').click(function() {
        let selected_options = $('.all_options option:selected');
        selected_options.remove().appendTo('.chosen_options');

        let body = document.getElementById('id_affiliation_offer_caps_body');

        for (let i = 0; i < selected_options.length; i++) {
            let offer = offers.filter(item => item[0] === selected_options[i].value)[0];
            let new_offer = document.createElement('tr');
            let html = '<tr>';
            html += '<td>' + offer[1] + '</td>';
            html += '<td><input type="text" id="editgoal_' + offer[0] + '" class="form-control input-sm edit_goals" value=""></td>';
            html += '<td><input type="text" id="s1payout_' + offer[0] + '" class="form-control input-sm s1_edit_payouts" value="" placeholder="' + offer[6] + '"/></td>';
            if (2 == offer[5]) {
                html += '<td><input type="text" id="s2payout_' + offer[0] + '" class="form-control input-sm s2_edit_payouts" value="" placeholder="' + offer[7] + '"/></td>';
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
