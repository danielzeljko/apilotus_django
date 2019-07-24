jQuery(document).ready(function(t) {
    function show_alert(content) {
        t(".billing_alert").html(content);
        t(".billing_alert").fadeIn(1000, function() {
            t(".billing_alert").fadeOut(3000)
        });
    }

    function show_waiting(d) {
        d ? t(".billing_waiting").html(loading_gif) : t(".billing_waiting").html("");
    }

    function format_date(year, month, date) {
        if (month < 10) month = "0" + month;
        if (date < 10) date = "0" + date;
        return month + "/" + date + "/" + year;
    }

    function set_dates() {
        t("#from_date").prop("disabled", true);
        t("#to_date").prop("disabled", true);
        let date = new Date;
        let cur_date = new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
        if ("date_thisweek" == date_type) {
            let r = cur_date.getDate() + 1;
            0 == cur_date.getDay() ? r -= 7 : r -= cur_date.getDay();
            cur_date.setDate(r);
            from_date = format_date(cur_date.getFullYear(), cur_date.getMonth() + 1, cur_date.getDate());
            r = cur_date.getDate() + 6;
            cur_date.setDate(r);
            to_date = format_date(cur_date.getFullYear(), cur_date.getMonth() + 1, cur_date.getDate());
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
                url: "/admin/api/billing_affiliate",
                data: {},
                success: function (response) {
                    show_waiting(false);
                    affiliations = response;

                    t.ajax({
                        type: "GET",
                        url: "/admin/ajax_billing_result_list",
                        data: {
                            from_date: t("#from_date").val(),
                            to_date: t("#to_date").val()
                        },
                        success: function(response) {
                            show_waiting(false);
                            billing_results = response;

                            if (0 === billing_results.length) {
                                show_alert("There is no billing result.");
                                return;
                            }

                            let html = "";

                            for (let i = 0; i < affiliations.length; i++) {
                                let affiliate = affiliations[i];
                                let afid = affiliate['afid'].split(', ');
                                let total = 0;
                                for (let j = 0; j < billing_results.length; j++) {
                                    let billing_result = billing_results[j];

                                    let trial_results = jQuery.parseJSON(billing_result['trial_result'].replace(new RegExp("'", 'g'), '"'));
                                    let mc_results = jQuery.parseJSON(billing_result['mc_result'].replace(new RegExp("'", 'g'), '"'));

                                    for (let k = 0; k < afid.length; k++) {
                                        for (let l = 0; l < trial_results.length; l++) {
                                            let result = trial_results[l];
                                            let afid_id = afid[k].split('(')[0];
                                            let cpa = afid[k].split('(')[1];
                                            cpa = cpa.substring(0, cpa.length - 1);
                                            if (afid_id === result['id']) {
                                                total += result['initial_customers'] * cpa.split(',')[0];
                                            }
                                        }
                                    }
                                    for (let k = 0; k < afid.length; k++) {
                                        for (let l = 0; l < mc_results.length; l++) {
                                            let result = mc_results[l];
                                            let afid_id = afid[k].split('(')[0];
                                            let cpa = afid[k].split('(')[1];
                                            cpa = cpa.substring(0, cpa.length - 1);
                                            if (afid_id === result['id']) {
                                                total += result['initial_customers'] * (cpa.split(',').length > 1 ? cpa.split(',')[1] : cpa);
                                            }
                                        }
                                    }
                                }

                                html += '<div class="col-lg-4 col-md-6 col-sm-12 col-xs-12 c_item"><div>';
                                html += '<button type="button" class="btn btn-link btn-sm payment_badge_blue" style="font-size: 18px; font-weight: bold; padding-left: 0;">' + affiliate['name'] + '</button>';
                                html += '<p>AFIDS: ' + affiliate['afid'] + '</p>';
                                html += '<p style="margin-top: 5px;">Total To Invoice: $ ' + total.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,') + '</p>';

                                html += '<h4 style="color: #6772e5">Sales Progress</h4>';
                                html += '<div class="row c_cnt_header">';
                                html += '<div style="color: #6772e5; text-align: center;" class="col-lg-5 col-md-5 col-sm-5 col-xs-5">OFFER</div>';
                                html += '<div style="color: #6772e5" class="col-lg-2 col-md-2 col-sm-2 col-xs-2">SALES</div>';
                                html += '<div style="color: #6772e5" class="col-lg-2 col-md-2 col-sm-2 col-xs-2">CPA</div>';
                                html += '<div style="color: #6772e5" class="col-lg-3 col-md-3 col-sm-3 col-xs-3">TOTAL</div>';
                                html += '</div>';
                                html += '<div class="c_cnt_list">';

                                for (let j = 0; j < billing_results.length; j++) {
                                    let billing_result = billing_results[j];

                                    let trial_results = jQuery.parseJSON(billing_result['trial_result'].replace(new RegExp("'", 'g'), '"'));
                                    let mc_results = jQuery.parseJSON(billing_result['mc_result'].replace(new RegExp("'", 'g'), '"'));
                                    let trial_count = 0;
                                    let mc_count = 0;
                                    let trial_cpa = 0;
                                    let mc_cpa = 0;

                                    for (let k = 0; k < afid.length; k++) {
                                        for (let l = 0; l < trial_results.length; l++) {
                                            let result = trial_results[l];
                                            let afid_id = afid[k].split('(')[0];
                                            let cpa = afid[k].split('(')[1];
                                            cpa = cpa.substring(0, cpa.length - 1);
                                            if (afid_id === result['id']) {
                                                trial_cpa = cpa.split(',')[0];
                                                trial_count += result['initial_customers'];
                                            }
                                        }
                                    }
                                    for (let k = 0; k < afid.length; k++) {
                                        for (let l = 0; l < mc_results.length; l++) {
                                            let result = mc_results[l];
                                            let afid_id = afid[k].split('(')[0];
                                            let cpa = afid[k].split('(')[1];
                                            cpa = cpa.substring(0, cpa.length - 1);
                                            if (afid_id === result['id']) {
                                                mc_cpa = (cpa.split(',').length > 1 ? cpa.split(',')[1] : cpa);
                                                mc_count += result['initial_customers'];
                                            }
                                        }
                                    }

                                    let offer = offers.filter(item => item['id'] === billing_result['offer_id'])[0];
                                    if (affiliate['name'] === "MaxBounty") {
                                        if (trial_count > 0 || mc_count > 0) {
                                            html += '<div class="row">';
                                            html += '<div style="text-align: center" class="col-lg-5 col-md-5 col-sm-5 col-xs-5">' + offer['name'] + '</div>';
                                            html += '<div style="text-align: center" class="col-lg-2 col-md-2 col-sm-2 col-xs-2">' + (trial_count + mc_count) + '</div>';
                                            html += '<div class="col-lg-2 col-md-2 col-sm-2 col-xs-2">$ ' + trial_cpa + '.00</div>';
                                            html += '<div class="col-lg-3 col-md-3 col-sm-3 col-xs-3">$ ' + (trial_count * trial_cpa + mc_count * mc_cpa).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,') + '</div>';
                                            html += '</div>';
                                        }
                                    }
                                    else {
                                        if (trial_count > 0) {
                                            html += '<div class="row">';
                                            html += '<div style="text-align: center" class="col-lg-5 col-md-5 col-sm-5 col-xs-5">' + offer['name'] + ' Trial</div>';
                                            html += '<div style="text-align: center" class="col-lg-2 col-md-2 col-sm-2 col-xs-2">' + trial_count + '</div>';
                                            html += '<div class="col-lg-2 col-md-2 col-sm-2 col-xs-2">$ ' + trial_cpa + '.00</div>';
                                            html += '<div class="col-lg-3 col-md-3 col-sm-3 col-xs-3">$ ' + (trial_count * trial_cpa).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,') + '</div>';
                                            html += '</div>';
                                        }
                                        if (mc_count > 0) {
                                            html += '<div class="row">';
                                            html += '<div style="text-align: center" class="col-lg-5 col-md-5 col-sm-5 col-xs-5">' + offer['name'] + ' MC</div>';
                                            html += '<div style="text-align: center" class="col-lg-2 col-md-2 col-sm-2 col-xs-2">' + mc_count + '</div>';
                                            html += '<div class="col-lg-2 col-md-2 col-sm-2 col-xs-2">$ ' + mc_cpa + '.00</div>';
                                            html += '<div class="col-lg-3 col-md-3 col-sm-3 col-xs-3">$ ' + (mc_count * mc_cpa).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,') + '</div>';
                                            html += '</div>';
                                        }
                                    }
                                }
                                html += '</div></div></div>';
                            }
                            t(".div_billing_body").html(html);
                        },
                        failure: function() {
                            show_waiting(false);
                            show_alert("Cannot load Affiliate Sales Goal information.")
                        }
                    });
                },
                failure: function () {
                    show_waiting(false);
                    show_alert("Offers cannot be loaded.");
                }
            });
        }
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async function get_export_result() {
        // for (let i = 0; i < affiliations.length; i++) {
        //     window.location.href = "/admin/export_billing_report/?affiliate_id=" + affiliations[i]['id'] + "&from_date=" + t("#from_date").val() + "&to_date=" + t("#to_date").val();
        //     await sleep(2000);
        // }
        window.location.href = "/admin/export_billing_reports/?from_date=" + t("#from_date").val() + "&to_date=" + t("#to_date").val();
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
        get_export_result();
    });


    let loading_gif = '<img src="/static/images/loading.gif" style="width: 22px; height: 22px;">';
    let from_date = "";
    let to_date = "";
    let billing_results = null;
    let date_type = "date_thisweek";
    let offers = null;
    let affiliations = null;

    set_dates();
    get_offer_list();
    get_billing_list();

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
});
