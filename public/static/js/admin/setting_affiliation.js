jQuery(document).ready(function (t) {
    function show_alert(type, content) {
        if ("main" === type) {
            $(".affiliation_alert").html(content);
            $(".affiliation_alert").fadeIn(1e3, function () {
                $(".affiliation_alert").fadeOut(3e3);
            });
        }
        else if ("add" === type) {
            $(".affiliation_add_alert").html(content);
            $(".affiliation_add_alert").fadeIn(1e3, function () {
                $(".affiliation_add_alert").fadeOut(3e3);
            });
        }
        else if ("edit" === type) {
            $(".affiliation_edit_alert").html(content);
            $(".affiliation_edit_alert").fadeIn(1e3, function () {
                $(".affiliation_edit_alert").fadeOut(3e3);
            });
        }
    }

    function show_waiting(type, status) {
        if ("main" === type)
            status ? $(".affiliation_waiting").html(loading_gif) : $(".affiliation_waiting").html("");
        else if ("edit" === type)
            status ? $(".affiliate_edit_waiting").html(loading_gif) : $(".affiliate_edit_waiting").html("");
    }

    function get_offer_list() {
        show_waiting("main", true);
        t.ajax({
            type: "GET",
            url: "../daemon/ajax_admin/offer_list.php",
            data: {},
            success: function (e) {
                show_waiting("main", false);
                if ("no_cookie" === e)
                    window.location.href = "../../admin/login.php";
                else if ("error" === e) {
                    show_alert("main", "Offers cannot be loaded.");
                }
                else {
                    all_offers = jQuery.parseJSON(e);
                }
            },
            failure: function () {
                show_waiting("main", false);
                show_alert("main", "Offers cannot be loaded.");
            }
        })
    }

    function get_affiliation_list() {
        show_waiting("main", true);
        $(".table_affiliation_body").html("");
        t.ajax({
            type: "GET",
            url: "../daemon/ajax_admin/setting_affiliation_list.php",
            data: {},
            success: function (e) {
                show_waiting("main", false);
                if ("no_cookie" === e)
                    return void (window.location.href = "../../admin/login.php");

                results = jQuery.parseJSON(e);
                show_filtered_list();
            },
            failure: function () {
                show_waiting("main", false);
                show_alert("main", "Cannot load affiliate goal information.");
            }
        })
    }

    function add_affiliate(offer_ids, offer_goals, s1_payouts, s2_ids, s2_payouts) {
        show_waiting("main", true);
        $.ajax({
            type: "GET",
            url: "../daemon/ajax_admin/setting_affiliation_add.php",
            data: {
                name: $(".add_affiliation_name").val(),
                afid: $(".add_affiliation_afid").val(),
                offer_ids: offer_ids,
                offer_goals: offer_goals,
                s1_payouts: s1_payouts,
                s2_ids: s2_ids,
                s2_payouts: s2_payouts
            },
            success: function (status) {
                show_waiting("main", false);
                if ("error" == status)
                    show_alert("main", "Affiliate cannot be added.");
                else if ("no_cookie" == status)
                    window.location.href = "../../admin/login.php";
                else if ("success" == status)
                    get_affiliation_list();
            },
            failure: function () {
                show_waiting("main", false);
                show_alert("main", "Affiliate cannot be added.");
            }
        });
    }

    function edit_affiliate(offer_ids, offer_goals, s1_payouts, s2_ids, s2_payouts) {
        show_waiting("main", true);
        $.ajax({
            type: "GET",
            url: "../daemon/ajax_admin/setting_affiliation_edit.php",
            data: {
                affiliate_id: affiliate_id,
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
                else if ("success" == status)
                    get_affiliation_list();
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
            url: "../daemon/ajax_admin/setting_affiliation_delete.php",
            data: {
                affiliate_id: affiliate_id
            },
            success: function (status) {
                show_waiting("main", false);
                if ("error" == status)
                    show_alert("main", "Affiliate cannot be deleted.");
                else if ("no_cookie" == status)
                    window.location.href = "../../admin/login.php";
                else if ("success" == status)
                    get_affiliation_list();
            },
            failure: function () {
                show_waiting("main", false);
                show_alert("main", "Affiliate cannot be deleted.");
            }
        });
    }

    function get_affiliate_offers() {
        show_waiting("edit", true);
        $.ajax({
            type: "GET",
            url: "../daemon/ajax_admin/setting_affiliation_offer_list.php",
            data: {
                affiliate_id: affiliate_id
            },
            success: function (data) {
                show_waiting("edit", false);
                if ("error" == data)
                    show_alert("edit", "Affiliate offers cannot be loaded.");
                else if ("no_cookie" == data)
                    window.location.href = "../../admin/login.php";
                else {
                    let offers = jQuery.parseJSON(data);
                    let all_options = '';
                    let chosen_options = '';
                    for (let i = 0; i < all_offers.length; i++) {
                        if (offers.includes(all_offers[i][0]))
                            chosen_options += '<option value="' + all_offers[i][0] + '">' + all_offers[i][1] + '</option>';
                        else
                            all_options += '<option value="' + all_offers[i][0] + '">' + all_offers[i][1] + '</option>';
                    }
                    $(".all_options").html(all_options);
                    $(".chosen_options").html(chosen_options);
                }
            },
            failure: function () {
                show_waiting("edit", false);
                show_alert("edit", "Affiliate offers cannot be loaded.");
            }
        });
    }

    function show_filtered_list() {
        let data = results;
        if (0 != crm_main_id)
            data = results.filter(function f(item) {
                let sub = item[1].filter(i => i[5] === crm_main_id);
                return sub.length > 0;
            });
        if (0 != vertical_main_id)
            data = results.filter(function f(item) {
                let sub = item[1].filter(i => i[6] === vertical_main_id);
                return sub.length > 0;
            });
        if (search_keyword)
            data = results.filter(function f(item) {
                if (item[0][1].toLowerCase().includes(search_keyword.toLowerCase()) ||
                    item[0][2].toLowerCase().includes(search_keyword.toLowerCase()))
                    return true;
                let sub = item[1].filter(i => i[3].toLowerCase().includes(search_keyword.toLowerCase()) ||
                    i[4].toLowerCase().includes(search_keyword.toLowerCase()) || i[1].includes(search_keyword));
                return sub.length > 0;
            });

        let html = "";
        for (let i = 0; i < data.length; i++) {
            let affiliate = data[i];
            html += '<tr>';
            html += '<td><button type="button" class="btn btn-link btn-sm btn_affiliation_edit payment_badge_blue" id="aedit_' + i + '" data-toggle="modal" data-target="#affiliation_edit_modal" style="font-size: inherit">' + affiliate[0][1] + '</div></button>';
            if (null == affiliate[0][2])
                html += '<td></td>';
            else
                html += '<td style="vertical-align: middle">' + affiliate[0][2] + '</td>';
            html += '<td></td>';
            html += '<td></td>';
            html += '<td><button type="button" class="btn btn-link btn-sm btn_affiliation_edit" id="gedit_' + i + '" data-toggle="modal" data-target="#affiliation_edit_modal"><span class="glyphicon glyphicon-list" aria-hidden="true"></span>&nbsp;Edit</button></td>';
            html += '</tr>';
            for (let j = 0; j < affiliate[1].length; j++) {
                let offer = affiliate[1][j];
                html += '<tr>';
                html += "<td></td>";
                html += "<td></td>";
                html += "<td>" + offer[3] + "</td>";
                html += "<td>" + offer[4] + "</td>";
                html += "<td>" + offer[1] + "</td>";
                html += '</tr>';
            }
        }
        $(".table_affiliation_body").html(html);
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

    function make_html(offers) {
        let html = '<table id="id_affiliation_offer_caps_table" class="table table-hover"' + (0 === offers.length ? ' style="display:none"' : "") + '>';
        html += '<thead id="id_affiliation_offer_caps_header"><tr>' +
            '<th>Offer Name</th>' +
            '<th>Offer Cap</th>' +
            '<th>Step1 CPA</th>';
        for (let i = 0; i < offers.length; i++) {
            let offer = offers[i];
            let offer_type = all_offers.filter(item => item[0] == offer[2])[0][5];
            if (2 == offer_type) {
                html += '<th>Step2 CPA</th>';
                break;
            }
        }
        html += '</tr></thead>';
        html += '<tbody id="id_affiliation_offer_caps_body">';

        for (let i = 0; i < offers.length; i++) {
            let offer = offers[i];
            let offer_type = all_offers.filter(item => item[0] == offer[2])[0];
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

    function save_special_code() {
        show_waiting("edit", true);
        $.ajax({
            type: "GET",
            url: "../daemon/ajax_admin/setting_affiliation_save_special_code.php",
            data: {
                affiliate_id: affiliate_id,
                special_code: $('#edit_special_code').val()
            },
            success: function (status) {
                show_waiting("edit", false);
                if ("error" == status)
                    show_alert("main", "Affiliate cannot be deleted.");
                else if ("no_cookie" == status)
                    window.location.href = "../../admin/login.php";
                else if ("success" == status) {

                }
            },
            failure: function () {
                show_waiting("edit", false);
                show_alert("edit", "Special Code cannot be saved.");
            }
        });
    }

    $(".crm_main_dropdown_menu li").on("click", function() {
        crm_main_id = $(this).find("a").attr("id");
        $(".crm_main_toggle_button").html($(this).text() + ' <span class="caret"></span>');
        show_filtered_list();
    });
    $(".vertical_main_dropdown_menu li").on("click", function() {
        vertical_main_id = $(this).find("a").attr("id");
        $(".vertical_main_toggle_button").html($(this).text() + ' <span class="caret"></span>');
        show_filtered_list();
    });
    $(".search_affiliates").on("input", function () {
        search_keyword = $(this).val();
        show_filtered_list();
    });


    $(".btn_affiliation_add").click(function () {
        $(".add_affiliation_name").val("");
        $(".add_affiliation_afid").val("");
        let all_options = "";
        for (let i = 0; i < all_offers.length; i++)
            all_options += '<option value="' + all_offers[i][0] + '">' + all_offers[i][1] + '</option>';
        $(".left_options").html(all_options);
        $(".right_options").html("");
        $("#id_add_affiliation_offer_caps_table").css("display", "none");
        $("#id_add_affiliation_offer_caps_body").html("");
    });
    $(".modal_btn_affiliation_add").click(function () {
        if ("" == $(".add_affiliation_name").val()) {
            show_alert("add", "Please input Affiliate Name.");
            $(".add_affiliation_name").focus();
            return;
        }
        if ("" == $(".add_affiliation_afid").val()) {
            show_alert("add", "Please input AFIDs of Affiliate.");
            $(".add_affiliation_afid").focus();
            return;
        }
        if (false === check_afids($(".add_affiliation_afid").val())) {
            show_alert("add", "There is duplicates or incorrect ids in AFIDs. Please check again.");
            $(".add_affiliation_afid").focus();
            return;
        }

        $("#affiliation_add_modal").modal("toggle");

        let ids = [];
        let goals = [];
        let s1_payouts = [];
        let s2_ids = [];
        let s2_payouts = [];
        $(".add_goals").each(function () {
            ids.push($(this).prop("id").substring(8));
            goals.push("" == $(this).val() ? "0" : $(this).val());
        });
        $(".s1_add_payouts").each(function () {
            s1_payouts.push("" == $(this).val() ? "0" : $(this).val());
        });
        $(".s2_add_payouts").each(function () {
            s2_ids.push($(this).prop("id").substring(9));
            s2_payouts.push("" == $(this).val() ? "0" : $(this).val());
        });

        add_affiliate(ids.join(','), goals.join(','), s1_payouts.join(','), s2_ids.join(','), s2_payouts.join(','));
    });


    $(document).on("click", ".btn_affiliation_edit", function () {
        let all_options = "";
        for (let i = 0; i < all_offers.length; i++)
            all_options += '<option value="' + all_offers[i][0] + '">' + all_offers[i][1] + '</option>';
        $(".all_options").html(all_options);
        $(".chosen_options").html("");
        $(".affiliation_offer_caps").html("");

        selected_id = $(this).prop("id").substring(6);
        affiliate_id = results[selected_id][0][0];
        $(".edit_affiliation_name").val(results[selected_id][0][1]);
        $(".edit_affiliation_afid").val(results[selected_id][0][2]);
        $("#edit_special_code").val(results[selected_id][0][3]);

        $(".affiliation_offer_caps").html(make_html(results[selected_id][1]));

        get_affiliate_offers();
    });
    $(".modal_btn_affiliation_edit").click(function () {
        if ("" == $(".edit_affiliation_name").val()) {
            show_alert("edit", "Please input Affiliate Name.");
            $(".edit_affiliation_name").focus();
            return;
        }
        if ("" == $(".edit_affiliation_afid").val()) {
            show_alert("edit", "Please input AFIDs of Affiliate.");
            $(".edit_affiliation_afid").focus();
            return;
        }
        if (false === check_afids($(".edit_affiliation_afid").val())) {
            show_alert("edit", "There is duplicates or incorrect ids in AFIDs. Please check again.");
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


    function refresh_table(add="") {
        let chosen_options = null;
        if ("" === add)
            chosen_options = $('.chosen_options option');
        else
            chosen_options = $('.right_options option');

        if (chosen_options.length > 0)
            $("#id_" + add + "affiliation_offer_caps_table").css("display", "table");
        else
            $("#id_" + add + "affiliation_offer_caps_table").css("display", "none");

        let html = '<tr>' +
            '<th>Offer Name</th>' +
            '<th>Offer Cap</th>' +
            '<th>Step1 CPA</th>';
        for (let i = 0; i < chosen_options.length; i++) {
            let offer = all_offers.filter(item => item[0] == chosen_options[i].value)[0];
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
            let offer = all_offers.filter(item => item[0] == selected_options[i].value)[0];
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

    $('.add_to_right').click(function() {
        let selected_options = $('.left_options option:selected');
        selected_options.remove().appendTo('.right_options');

        let body = document.getElementById('id_add_affiliation_offer_caps_body');

        for (let i = 0; i < selected_options.length; i++) {
            let offer = all_offers.filter(item => item[0] == selected_options[i].value)[0];
            let new_offer = document.createElement('tr');
            let html = '<tr>';
            html += '<td>' + offer[1] + '</td>';
            html += '<td><input type="text" id="addgoal_' + offer[0] + '" class="form-control input-sm add_goals" value=""></td>';
            html += '<td><input type="text" id="s1payout_' + offer[0] + '" class="form-control input-sm s1_add_payouts" value="" placeholder="' + offer[6] + '"/></td>';
            if (2 == offer[5]) {
                html += '<td><input type="text" id="s2payout_' + offer[0] + '" class="form-control input-sm s2_add_payouts" value="" placeholder="' + offer[7] + '"/></td>';
            }
            html += '</tr>';
            new_offer.innerHTML = html;
            body.appendChild(new_offer);
        }
        refresh_table("add_");
    });
    $('.remove_to_left').click(function() {
        let selected_options = $('.right_options option:selected');
        selected_options.remove().appendTo('.left_options');

        for (let i = 0; i < selected_options.length; i++) {
            $("#addgoal_" + selected_options[i].value).parent().parent().remove();
        }
        refresh_table("add_");
    });

    $('.modal_btn_special_code_reset').click(function () {
        let rand_str = '01234567890123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        let special_code = '';
        for (let i = 0; i < 16; i++) {
            special_code += rand_str[Math.floor(Math.random() * rand_str.length)];
        }
        $("#edit_special_code").val(special_code);

        let result = results[selected_id];
        result[0][3] = special_code;

        save_special_code();
    });

    $('.modal_btn_special_code_copy').click(function () {
        let special_code = document.getElementById("edit_special_code");
        special_code.select();
        document.execCommand("copy");
    });

    let loading_gif = '<img src="../images/loading.gif" style="width:22px;height:22px;">';
    let results = null;
    let all_offers = null;
    let affiliate_id = -1;
    let selected_id = -1;
    let search_keyword = '';
    let crm_main_id = 0;
    let vertical_main_id = 0;

    get_offer_list();
    get_affiliation_list();
});
