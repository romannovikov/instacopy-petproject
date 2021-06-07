function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Check if this cookie string begin with the name we want
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function csrf() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    })
}

function parseBool(str) {
    // console.log(typeof str);
    // strict: JSON.parse(str)

    if (str == null)
        return false;

    if (typeof str === 'boolean') {
        return (str === true);
    }

    if (typeof str === 'string') {
        if (str == "")
            return false;

        str = str.replace(/^\s+|\s+$/g, '');
        if (str.toLowerCase() == 'true' || str.toLowerCase() == 'yes')
            return true;

        str = str.replace(/,/g, '.');
        str = str.replace(/^\s*\-\s*/g, '-');
    }

    // var isNum = string.match(/^[0-9]+$/) != null;
    // var isNum = /^\d+$/.test(str);
    if (!isNaN(str))
        return (parseFloat(str) != 0);

    return false;
}

function savedToggle() {
    $("form.saved-form").each(function () {
        $(this).on('submit', function (e) {
            e.preventDefault();
            var requestUrl = $(this).attr("action");
            var objId = $(this).find('input[name="data-obj-id"]').val();
            var isSaved = $(this).find('input[name="data-is-saved"]').val();
            var data = {
                "object_id": objId,
                "is_saved": parseBool(isSaved)
            };

            $.ajax({
                url: requestUrl,
                method: "POST",
                data: {
                    json_data: JSON.stringify(data)
                },
                success: function (data) {
                    if (data.is_saved == true) {
                        $('#saved-form-' + objId).find('input[name="data-is-saved"]').attr('value', 'True');
                        $('#saved-btn-' + objId).html('<span class="icon is-small"><i class="fas fa-bookmark"></i></span>');
                    } else {
                        $('#saved-form-' + objId).find('input[name="data-is-saved"]').attr('value', 'False');
                        $('#saved-btn-' + objId).html('<span class="icon is-small"><i class="far fa-bookmark"></i></span>');
                    }
                },
                error: function (data) {
                    console.log(data.status + ' ' + data.message);
                }
            })
        })
    })
}

function likeToggle() {
    $("form.like-form").each(function () {
        $(this).on('submit', function (e) {
            e.preventDefault();
            var requestUrl = $(this).attr("action");
            var objContentType = $(this).find('input[name="data-obj-content-type"]').val();
            var objId = $(this).find('input[name="data-obj-id"]').val();
            var isLiked = $(this).find('input[name="data-is-liked"]').val();
            var data = {
                "object_content_type": objContentType,
                "object_id": objId,
                "is_liked": parseBool(isLiked)
            };
            var likeCount = $('#like-counter-' + objId).attr("data-like-count");

            $.ajax({
                url: requestUrl,
                method: "POST",
                data: {
                    json_data: JSON.stringify(data)
                },
                success: function (data) {
                    if (data.is_liked == true) {
                        $('#like-form-' + objId).find('input[name="data-is-liked"]').attr('value', 'True');
                        $('#like-btn-' + objId).html('<span class="icon is-small"><i class="fas fa-heart"></i></span>');
                        $('#like-counter-' + objId).attr("data-like-count", String(parseInt(likeCount) + 1));
                        $('#like-counter-' + objId).html("<strong><small>" + String(parseInt(likeCount) + 1) + " likes</small></strong>");
                    } else {
                        $('#like-form-' + objId).find('input[name="data-is-liked"]').attr('value', 'False');
                        $('#like-btn-' + objId).html('<span class="icon is-small"><i class="far fa-heart"></i></span>');
                        $('#like-counter-' + objId).attr("data-like-count", String(parseInt(likeCount) - 1));
                        $('#like-counter-' + objId).html("<strong><small>" + String(parseInt(likeCount) - 1) + " likes</small></strong>");
                    }
                },
                error: function (data) {
                    console.log(data.status + ' ' + data.message);
                }
            })
        })

    })
}

function followToggle() {
    $("form.follow-form").each(function () {
        $(this).on('submit', function (e) {
            e.preventDefault();
            var requestUrl = $(this).attr("action");
            var followedId = $(this).find('input[name="data-followed-id"]').val();
            var isFollowed = $(this).find('input[name="data-is-followed"]').val();

            var followerCount = $('#follower-counter-' + followedId).attr("data-follower-count");

            var data = {
                "followed_id": followedId,
                "is_followed": parseBool(isFollowed)
            };

            $.ajax({
                url: requestUrl,
                method: "POST",
                data: {
                    json_data: JSON.stringify(data)
                },
                success: function (data) {
                    if (data.is_followed == true) {
                        $('#follow-form-' + followedId).find('input[name="data-is-followed"]').attr('value', 'True');
                        $('#follow-btn-' + followedId).attr('class', 'button is-info is-light is-small follow-btn');
                        $('#follow-btn-' + followedId).text('Unfollow');
                        $('#follower-counter-' + followedId).attr("data-follower-count", String(parseInt(followerCount) + 1));
                        $('#follower-counter-' + followedId).html("<p><strong>" + String(parseInt(followerCount) + 1) + "</strong> followers</p>");
                    } else {
                        $('#follow-form-' + followedId).find('input[name="data-is-followed"]').attr('value', 'False');
                        $('#follow-btn-' + followedId).attr('class', 'button is-info is-small follow-btn');
                        $('#follow-btn-' + followedId).text('Follow');
                        $('#follower-counter-' + followedId).attr("data-follower-count", String(parseInt(followerCount) - 1));
                        $('#follower-counter-' + followedId).html("<p><strong>" + String(parseInt(followerCount) - 1) + "</strong> followers</p>");
                    }
                },
                error: function (data) {
                    console.log(data.status + ' ' + data.message);
                }
            })
        })
    })
}


$(document).ready(function () {
    csrf()
    savedToggle()
    likeToggle()
    followToggle()
});
