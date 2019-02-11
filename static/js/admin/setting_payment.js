jQuery( document ).ready(function( $ ) 
{

    //var spinner = '<p><div class="spinner"><div class="bounce1"></div><div class="bounce2"></div><div class="bounce3"></div></div></p>';
    var spinner = '<img src="../images/loading.gif" style="width:22px;height:22px;">';

    var card_id = '';
    var expiry_month = '';
    var expiry_year = '';

    var customer_id = '';
    var subscription_id = '';

    var stripe = Stripe('pk_test_kyxgtxD5BcPyVARUJbiRgQCN');
    //var stripe = Stripe('pk_live_y00zEB5AHQZO1u9ln9Sv3Kdg');
    var elements = stripe.elements();
    
    var cardNumber;
    var cardExpiry;
    var cardCvc;

    var card_init = true;
    var card_valid = false;


    
    init();


    function init()
    {
        initAjax();

        var style = {
            base: {
                color: '#303238',
                fontSize: '15px',
                lineHeight: '34px',
                fontSmoothing: 'antialiased',
                '::placeholder': {
                    color: '#d9d9d9',
                },
            },
            invalid: {
                color: '#e5424d',
                ':focus': {
                    color: '#303238',
                },
            },
        };

        cardNumber = elements.create('cardNumber', {style: style});
        cardExpiry = elements.create('cardExpiry', {style: style});
        cardCvc = elements.create('cardCvc', {style: style});

        cardNumber.mount('#card_number');
        cardExpiry.mount('#card_expiry');
        cardCvc.mount('#card_cvc');
    }

    function initAjax() 
    {
        card_init = true;
        card_valid = false;

        ajaxCardInfo();
        ajaxSubscriptionInfo();
        ajaxPaymentHistory();
    }

    // Change event of Credit Card Number input
    cardNumber.addEventListener('change', function(event) 
    {
        card_init = false;

        if (event.empty == true)
        {
            $('#warning_card_number').html('You can\'t leave this empty.');
            return;
        }

        if (event.error) 
            $('#warning_card_number').html(event.error.message);
        else
            $('#warning_card_number').html('');
    });

    // Change event of Expiry Date input
    cardExpiry.addEventListener('change', function(event) 
    {
        card_init = false;

        if (event.empty == true)
        {
            $('#warning_expiry_date').html('You can\'t leave this empty.');
            return;
        }

        if (event.error) 
            $('#warning_expiry_date').html(event.error.message);
        else
            $('#warning_expiry_date').html('');
    });

    // Change event of CVC Number input
    cardCvc.addEventListener('change', function(event) 
    {
        card_init = false;

        if (event.empty == true)
        {
            $('#warning_cvc_number').html('You can\'t leave this empty.');
            return;
        }

        if (event.error) 
            $('#warning_cvc_number').html(event.error.message);
        else
            $('#warning_cvc_number').html('');
    });

    // Click New Card Button
    $('#card_buttons').on('click', '#btn_new_card', function (e)
    {
        $('#new_card_modal').modal('show');
    });

    $('#modal_btn_new_card').click(function ()
    {
        if (card_init)
        {
            $('#warning_card_number').html('You can\'t leave this empty.');
            $('#warning_expiry_date').html('You can\'t leave this empty.');
            $('#warning_cvc_number').html('You can\'t leave this empty.');

            return;
        }

        if ($('#warning_card_number').html() == '' && $('#warning_expiry_date').html() == '' && $('#warning_cvc_number').html() == '')
        {
            $('#new_card_modal').modal('hide');
            $('#waiting_modal').modal('show');

            stripe.createToken(cardNumber).then(function(result) 
            {
                if (result.token)
                {
                    $.ajax(
                    {
                        type : 'GET',
                        url : '../daemon/ajax_admin/payment_card_new.php',
                        data : {
                            'token_id' : result.token.id,
                            'card_id' : result.token.card.id
                        },
                        success:function(response)
                        {
                            $('#waiting_modal').modal('hide');

                            if (response == 'success')
                                initAjax();
                            else if (response == 'no_cookie')
                            {
                                window.location.href = '../../admin/login.php';
                                return;
                            }
                            else
                                alert('New Card Error!');
                        },
                        failure:function(response) 
                        {
                            $('#waiting_modal').modal('hide');
                            alert('New Card Error!');
                        }
                    });
                }
                else
                    $('#waiting_modal').modal('hide');
            });
        }
    });

    // Click Edit Card Button
    $('#card_buttons').on('click', '#btn_edit_card', function (e)
    {
        $('#expiry_month').val(expiry_month);
        $('#expiry_year').val(expiry_year)

        $('#edit_card_modal').modal('show');
    });

    $('#modal_btn_edit_card').click(function ()
    {
        $('#edit_card_modal').modal('hide');

        $.ajax(
        {
            type : 'GET',
            url : '../daemon/ajax_admin/payment_card_update.php',
            data : {
                'expiry_month' : $('#expiry_month').val(),
                'expiry_year' : $('#expiry_year').val()
            },
            success:function(response)
            {
                if (response == 'success')
                    initAjax();
                else if (response == 'no_cookie')
                {
                    window.location.href = '../../admin/login.php';
                    return;
                }
                else
                    alert('Edit card error!');
            },
            failure:function(response) 
            {
                
            }
        });
    });

    // Click Delete Card Button
    $('#card_buttons').on('click', '#btn_delete_card', function (e)
    {
        $('#delete_card_modal').modal('show');
    });

    $('#modal_btn_delete_card').click(function ()
    {
        $('#delete_card_modal').modal('hide');

        $.ajax(
        {
            type : 'GET',
            url : '../daemon/ajax_admin/payment_card_delete.php',
            data : { },
            success:function(response)
            {
                if (response == 'success')
                    initAjax();
                else if (response == 'no_cookie')
                {
                    window.location.href = '../../admin/login.php';
                    return;
                }
                else
                    alert('Delete card error!');
            },
            failure:function(response) 
            {
                
            }
        });
    });

    // Click New Subscription Button
    $('#subscription_buttons').on('click', '#btn_new_subscription', function (e)
    {
        if (!card_valid)
        {
            alert('Please add card first and try it again.');
            return;
        }

        $('.setting_subscription_waiting').html(spinner);

        $.ajax(
        {
            type : 'GET',
            url : '../daemon/ajax_admin/payment_plan_get.php',
            data : { },
            success:function(response)
            {
                $('.setting_subscription_waiting').html('');

                var obj = jQuery.parseJSON(response);

                if (obj[0] == 'success')
                {
                    $('#plan_name').val(obj[1].id);
                    $('#plan_price').val('$' + (obj[1].amount / 100));
                    $('#plan_interval').val(obj[1].interval);

                    $('#new_subscription_modal').modal('show');
                }
                else if (obj[0] == 'no_cookie')
                {
                    window.location.href = '../../admin/login.php';
                    return;
                }
                else
                {
                    alet('Cannot get plan for subscription.');
                }
            },
            failure:function(response) 
            {
                $('.setting_subscription_waiting').html('');
            }
        });
    });

    $('#modal_btn_new_subscription').click(function ()
    {
        $('#new_subscription_modal').modal('hide');
        $('#waiting_modal').modal('show');

        $.ajax(
        {
            type : 'GET',
            url : '../daemon/ajax_admin/payment_subscription_new.php',
            data : { },
            success:function(response)
            {
                $('#waiting_modal').modal('hide');

                if (response == 'success')
                    initAjax();
                else if (response == 'no_cookie')
                {
                    window.location.href = '../../admin/login.php';
                    return;
                }
                else
                    alert('New subscription error!');
            },
            failure:function(response) 
            {
                $('#waiting_modal').modal('hide');                
            }
        });
    });

    // Click Cancel Subscription Button
    $('#subscription_buttons').on('click', '#btn_cancel_subscription', function (e)
    {
        $('#cancel_subscription_modal').modal('show');
    });

    $('#modal_btn_cancel_subscription').click(function ()
    {
        $('#cancel_subscription_modal').modal('hide');

        $.ajax(
        {
            type : 'GET',
            url : '../daemon/ajax_admin/payment_subscription_cancel.php',
            data : { },
            success:function(response)
            {
                if (response == 'success')
                    initAjax();
                else if (response == 'no_cookie')
                {
                    window.location.href = '../../admin/login.php';
                    return;
                }
                else
                    alert('Cancel subscription error!');
            },
            failure:function(response) 
            {
                
            }
        });
    });

    function ajaxCardInfo() 
    {
        $('.setting_card_waiting').html(spinner);

        $.ajax(
        {
            type : 'GET',
            url : '../daemon/ajax_admin/payment_card_get.php',
            data : { },
            success:function(response)
            {
                $('.setting_card_waiting').html('');

                var obj = jQuery.parseJSON(response);
                var html;

                card_id = '';

                if (obj[0] == 'success')
                {
                    card_id = obj[1].id;
                    expiry_month = obj[1].exp_month;
                    expiry_year = obj[1].exp_year;

                    html = '<tr><th>Card Brand</th><th>' + obj[1].brand + '</th></tr>';
                    $('#table_card_head').html(html);

                    html  = '<tr><td>Country</td><td>' + obj[1].country + '</td></tr>';
                    html += '<tr><td>Card Number</td><td>**** **** **** ' + obj[1].last4 + '</td></tr>';
                    html += '<tr><td>Expiry Date</td><td>' + obj[1].exp_month + ' / ' + obj[1].exp_year + '</td></tr>';
                    if (obj[1].cvc_check == 'pass')
                    {
                        html += '<tr><td>CVC Check</td><td><span class="payment_badge payment_badge_blue">passed</span></td></tr>';
                        card_valid = true;
                    }
                    else
                        html += '<tr><td>CVC Check</td><td><span class="payment_badge payment_badge_red">' + obj[1].cvc_check + '</span></td></tr>';
                    html += '<tr><td>Card ID</td><td>' + obj[1].id + '</td></tr>';
                    $('#table_card_body').html(html);

                    html = '<button id="btn_new_card" type="button" class="btn btn-link btn-sm" disabled><span class="glyphicon glyphicon-plus-sign" aria-hidden="true"></span>&nbsp;New Card</button>';
                    html += '<button id="btn_edit_card" type="button" class="btn btn-link btn-sm"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span>&nbsp;Edit</button>';
                    html += '<button id="btn_delete_card" type="button" class="btn btn-link btn-sm"><span class="glyphicon glyphicon-minus-sign" aria-hidden="true" style="color: #ffa5a5"></span>&nbsp;Delete</button>';
                    $('#card_buttons').html(html);
                }
                else if (obj[0] == 'no_cookie')
                {
                    window.location.href = '../../admin/login.php';
                    return;
                }
                else
                {
                    $('#table_card_head').html('');
                    $('#table_card_body').html('');

                    html = '<button id="btn_new_card" type="button" class="btn btn-link btn-sm"><span class="glyphicon glyphicon-plus-sign" aria-hidden="true"></span>&nbsp;New Card</button>';
                    html += '<button id="btn_edit_card" type="button" class="btn btn-link btn-sm" disabled><span class="glyphicon glyphicon-edit" aria-hidden="true"></span>&nbsp;Edit</button>';
                    html += '<button id="btn_delete_card" type="button" class="btn btn-link btn-sm" disabled><span class="glyphicon glyphicon-minus-sign" aria-hidden="true" style="color: #ffa5a5"></span>&nbsp;Delete</button>';
                    $('#card_buttons').html(html);
                }
            },
            failure:function(response) 
            {
                $('.setting_card_waiting').html('');
            }
        });
    }

    function ajaxSubscriptionInfo()
    {
        $('.setting_subscription_waiting').html(spinner);

        $.ajax(
        {
            type : 'GET',
            url : '../daemon/ajax_admin/payment_subscription_get.php',
            data : { },
            success:function(response)
            {
                $('.setting_subscription_waiting').html('');

                var obj = jQuery.parseJSON(response);
                var html = '';

                if (obj[0] == 'success')
                {
                    html = '<tr><th>Plan Name</th><th>' + obj[1].plan.id + '</th></tr>';
                    $('#table_subscription_head').html(html);

                    html  = '<tr><td>Price</td><td>$' + (obj[1].plan.amount / 100) + '</td></tr>';
                    html += '<tr><td>Interval</td><td>' + obj[1].plan.interval + '</td></tr>';
                    html += '<tr><td>Subscription Created Date</td><td>' + ts2Date(obj[1].created) + '</td></tr>';
                    html += '<tr><td>Current Period Start</td><td>' + ts2Date(obj[1].current_period_start) + '</td></tr>';
                    html += '<tr><td>Current Period End</td><td>' + ts2Date(obj[1].current_period_end) + '</td></tr>';
                    if (obj[1].status == 'active')
                        html += '<tr><td>Subscription Status</td><td><span class="payment_badge payment_badge_blue">' + obj[1].status + '</span></td></tr>';
                    else
                        html += '<tr><td>Subscription Status</td><td><span class="payment_badge payment_badge_red">' + obj[1].status + '</span></td></tr>';
                    html += '<tr><td>Subscription ID</td><td>' + obj[1].id + '</td></tr>';
                    $('#table_subscription_body').html(html);

                    html = '<button id="btn_new_subscription" type="button" class="btn btn-link btn-sm" disabled><span class="glyphicon glyphicon-plus-sign" aria-hidden="true"></span>&nbsp;New Subscription</button>';
                    html += '<button id="btn_cancel_subscription" type="button" class="btn btn-link btn-sm"><span class="glyphicon glyphicon-minus-sign" aria-hidden="true" style="color: #ffa5a5"></span>&nbsp;Cancel</button>';
                    $('#subscription_buttons').html(html);
                }
                else if (obj[0] == 'no_cookie')
                {
                    window.location.href = '../../admin/login.php';
                    return;
                }
                else
                {
                    $('#table_subscription_head').html('');
                    $('#table_subscription_body').html('');

                    html = '<button id="btn_new_subscription" type="button" class="btn btn-link btn-sm"><span class="glyphicon glyphicon-plus-sign" aria-hidden="true"></span>&nbsp;New Subscription</button>';
                    html += '<button id="btn_cancel_subscription" type="button" class="btn btn-link btn-sm" disabled><span class="glyphicon glyphicon-minus-sign" aria-hidden="true" style="color: #ffa5a5"></span>&nbsp;Cancel</button>';
                    $('#subscription_buttons').html(html);
                }
            },
            failure:function(response) 
            {
                $('.setting_subscription_waiting').html('');
            }
        });
    }

    function ajaxPaymentHistory()
    {
        $('.setting_payment_waiting').html(spinner);

        $.ajax(
        {
            type : 'GET',
            url : '../daemon/ajax_admin/payment_invoices_get.php',
            data : { },
            success:function(response)
            {
                $('.setting_payment_waiting').html('');

                var obj = jQuery.parseJSON(response);
                var html = '';

                if (obj[0] == 'success')
                {
                    var invoice_count = obj[1].data.length;
                    for (var i = 0; i < invoice_count; i ++)
                    {
                        html += '<tr>';
                        html += '<td>' + (i + 1) + '</td>';
                        html += '<td>$' + (obj[1].data[i].amount_due / 100) + '</td>';
                        if (obj[1].data[i].paid == true)
                            html += '<td><span class="payment_badge payment_badge_cyan">Paid</span></td>';
                        else
                            html += '<td></td>';
                        html += '<td>' + ts2Date(obj[1].data[i].date) + '</td>';
                        html += '<td>' + ts2Date(obj[1].data[i].period_start) + ' - ' + ts2Date(obj[1].data[i].period_end) + '</td>';
                        html += '<td>' + obj[1].data[i].id + '</td>';
                        html += '</tr>';
                    }

                    $('#table_payment_body').html(html);
                }
                else if (obj[0] == 'no_cookie')
                {
                    window.location.href = '../../admin/login.php';
                    return;
                }
                else
                    $('#table_payment_body').html('');
            },
            failure:function(response) 
            {
                $('.setting_payment_waiting').html('');
            }
        });
    }

    function ts2Date(timestamp)
    {
        var date = new Date(timestamp * 1000);

        var year = date.getFullYear();
        var month = (date.getMonth() < 9 ? '0' : '') + (date.getMonth() + 1);
        var day = (date.getDate() < 10 ? '0' : '') + date.getDate();
        
        var hour = (date.getHours() < 10 ? '0' : '') + date.getHours();
        var minute = (date.getMinutes() < 10 ? '0' : '') + date.getMinutes();
        var second = (date.getSeconds() < 10 ? '0' : '') + date.getSeconds();

        return year + '/' + month + '/' + day + ' ' + hour + ':' + minute + ':' + second;
    }
});