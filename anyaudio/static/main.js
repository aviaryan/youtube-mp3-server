// search button on click
// gets search results
$('#searchBtn').click(function(){
	search_text = $('#search').val();
	// console.log(search_text);
	$('#loading_text').show();
	// remove old data
	search_temp = $('.search_result').first().clone();
	// reset
	search_temp.show();
	// stop loading previous audio
	// http://stackoverflow.com/questions/4071872/html5-video-force-abort-of-buffering
	search_temp.find('.webm-audio').attr('src', '');
	search_temp.find('.m4a-audio').attr('src', '');
	search_temp.find('audio').load();
	// set other defaults
	search_temp.find('.download').text('Get Link');
	search_temp.find('.download').attr('href', '#');
	search_temp.find('.download_mp3').text('Download MP3');
	search_temp.find('.download_mp3').attr('href', '#');
	search_temp.find('audio').hide();
	search_temp.find('.stream').show();
	search_temp.find('.stream').text('Stream');
	search_temp.find('.thumb').attr('src', 'http://placehold.it/480x360.png?text=AnyAudio');
	search_temp.unbind('click');
	// delete
	$('.search_result').remove();
	// get new results
	$.getJSON('/api/v2/search?q=' + search_text, success=function(data, textStatus, jqXHR){
		// create new
		data = data['results'];
		for (i=0; i<data.length; i++){
			search_x = search_temp.clone();
			search_x.attr('id', 'result' + i);
			// set values
			$(search_x).find('.thumb').attr('src', data[i]['thumb']);
			$(search_x).find('.thumb_link').attr('href', 'https://youtube.com/watch?v=' + data[i]['id']);
			$(search_x).find('.title').html(data[i]['title']);
			$(search_x).find('.length').text(data[i]['length']);
			$(search_x).find('.uploader').html(data[i]['uploader']);
			$(search_x).find('.time').text(data[i]['time']);
			$(search_x).find('.views').text(data[i]['views'] + ' views');
			$(search_x).find('.download').attr('data-get-url', data[i]['get_url']);
			$(search_x).find('.download').click(get_download_link);
			$(search_x).find('.download_mp3').attr(
				'data-api-link',
				'http://www.youtubeinmp3.com/fetch/?format=JSON&video=http://www.youtube.com/watch?v=' + data[i]['id']
			);
			$(search_x).find('.download_mp3').click(start_mp3_download);
			$(search_x).find('.stream').attr('data-stream-url', data[i]['stream_url']);
			$(search_x).find('.stream').click(start_streaming);
			// set d/l filename
			$(search_x).find('.download').attr('download', data[i]['title'] + '.m4a');
			// console.log(search_x);
			$(search_x).addClass('flex_force'); // just flex doesn't work
			search_x.appendTo('#container');
		}
		// hide loading
		$('#loading_text').hide();
	});
});

// gets the download link for a video
function get_download_link(event){
	event.preventDefault();
	elem = $(event.target);
	elem.text('Fetching...');
	elem.unbind('click');
	$.getJSON(elem.attr('data-get-url'), success=function(data, textStatus, jqXHR){
		if (data['status'] != 200){
			elem.text('Failed');
			elem.removeAttr('href');
			return false;
		}
		elem.text('Download (Right click -> Save As)');
		elem.click(download_start);
		elem.attr('href', data['url']);
		elem.attr('target', '_blank');
		return false;
	});
}

// starts the streaming
function start_streaming(event){
	event.preventDefault();
	elem = $(event.target);
	elem.text('Connecting...');
	elem.unbind('click');
	$.getJSON(elem.attr('data-stream-url'), success=function(data, textStatus, jqXHR){
		if (data['status'] != 200){
			elem.text('Failed');
			return false;
		}
		elem.hide();
		var audio = elem.siblings('audio');
		if (data['url'].search('audio%2Fwebm') > -1 || data['url'].search('audio/webm') > -1){
			audio.find('.webm-audio').attr('src', data['url']);
		} else {
			audio.find('.m4a-audio').attr('src', data['url']);
		}
		audio.show();
		audio.load();
		audio[0].play();  // audio comes as array
	});
	return false;
}

// start mp3 download
function start_mp3_download(event){
	event.preventDefault();
	elem = $(event.target);
	elem.text('Please wait...');
	elem.unbind('click');
	$.getJSON(elem.attr('data-api-link'), success=function(data, textStatus, jqXHR){
		elem.attr('href', data['link']);
		elem.text('Click to download');
	});
	return false;
}

// after download button is clicked
function download_start(event){
	$(event.target).text('Please wait');
	elem = $(event.target);
	setTimeout(function(){ // let the link activate
		elem.attr('href', '#');
		elem.removeAttr('download');
		elem.removeAttr('target'); // don't open new tab
		elem.unbind('click');
	}, 500);
}

$(document).ready(function(){
	$('.search_result').hide();
	$('#search').keyup(function(e){
		if(e.keyCode == 13){
			$(this).trigger("enterKey");
		}
	});

	$('#search').bind('enterKey', function(e){
		$('#searchBtn').click();
	});
});
