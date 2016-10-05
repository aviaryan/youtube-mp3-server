$(document).ready(function(){


	// initializing Stream Player
	var streamPlayer = plyr.setup(document.querySelector('#stream-player'));

	//Search event listener
	$('#ymp3-search').submit(function(e){
		var $this  = $(this);
		e.preventDefault();
		var searchInput = $this.find('.search-btn').val();
		console.log(searchInput);
		loadResult(searchInput);
	});

	//Fetches url and starts dowload in new tab
	$('body').on('click','.ymp3-download',function(e){
		e.preventDefault();
		$this = $(this);
		$this.addClass('dwn-ready-card');

		if($this.hasClass('dwn-done'))
			$this.removeClass('dwn-done');

		$.getJSON($this.attr('data-get-url'), success=function(data, textStatus, jqXHR){
			if (data['status'] != 200){
				$this.text('Failed');
				$this.removeAttr('href');
				return false;
			}
			console.log($this.attr('data-get-url'));
			window.open(data['url']);
			//window.location.href = data['url'];
			$this.addClass('dwn-done');
			$this.unbind('click');
		});
	});

	//Nav Overlay trigger
	$('#menu-bar').click(function(e){
		e.preventDefault();
		document.getElementById("nav-overlay").style.width = "100%";
	});


	$('#nav-overlay .closebtn').click(function(e){
		e.preventDefault();
		document.getElementById("nav-overlay").style.width = 0;
	});

	//Auto Suggestion on click
	$('.ymp3-search-input').keyup(function(){
		var $this = $(this),
			searchInput = $this.val();

		console.log(searchInput);

		//Aborts on no input and loads playlist item
		if (!searchInput && $this.siblings('.search-suggestions').hasClass('searching')) {
			$this.siblings('.search-suggestions').removeClass('searching');
			return;
		}
		else if(!searchInput)
			return;

		//Hides Playlist items
		$this.siblings('.search-suggestions').addClass('searching');

		loadAutoSuggest(searchInput);//Loads the auto suggest
	});

	//Loads results on clicking auto suggestion list item
	$('.nav--custom .search-suggestions').on('click','.search-suggestions-res a',function(e){
		e.preventDefault();
		var $this = $(this),
			searchInput = $(this).text().trim();

		$('.ymp3-search-input').val(searchInput);//Changes value of search bar
		loadAutoSuggest(searchInput);
		loadResult(searchInput);//Loads Results
		//console.log(searchInput);
	});

	//Loads results on clicking playlist item from auto suggestion
	$('.popular-suggestions').on('click','.popular-suggestions_res a',function(e){
		e.preventDefault();
		var $this = $(this),
			searchInput = $(this).text().trim();

		$('.ymp3-search-input').val(searchInput);//Changes value of search bar
		loadResult(searchInput,1);//Loads Playlist
		//console.log(searchInput);
	});

	$('body').on('click','.stream-btn a',function (e) {
		e.preventDefault();
		var streamUrl = $(this).data('stream-url');
		// $('#stream-player-modal').openModal();
		startStream(streamPlayer,streamUrl);
		// console.log("qrr");
	});
});
/*
Returns detail card
@param {object}: card data
@returns data{string}: card HTML
*/
function getCardHtml(data){
	return '<div class="col s6 m4 l3"><div class="card card--ym3"><a data-get-url="'+data['get_url']+'" class="card-image waves-effect waves-block waves-light ymp3-download"><img class="activator" src="'+data["thumb"]+'"><div class="card-overlay overlay--dark"></div><div class="meta-duration ">'+data["length"]+'</div><span href="#!" class="btn-dwn valign-wrapper"><i class="valign fa fa-spinner fa-pulse fa-3x fa-fw"></i><i class="valign fa fa-arrow-down" aria-hidden="true"></i><i class="valign fa fa-check fa-2x" aria-hidden="true"></i></span></a><div class="card-content"><span class="activator card--ym3--title flow-text">'+data["title"]+'</span><div class="meta"><div class="channel color-primary"><i class="fa fa-bullseye" aria-hidden="true"></i>'+data["uploader"]+'</div><div class="views color-primary"><i class="fa fa-eye" aria-hidden="true"></i>'+data["views"]+'</div></div><div class="stream-btn"><a data-stream-url="'+data['stream_url']+'" class="tooltipped modal-trigger" data-position="bottom" data-delay="50" data-tooltip="I am tooltip" href="#stream-player"><i class="fa fa-play-circle-o" aria-hidden="true"></i></a></div></div><div class="card-reveal"><span class="card-title color-primary activator"><i class="fa fa-times right"></i>'+data["title"]+'</span><p class="flow-text">'+data['description']+'</p></div></div></div>';
}

/*
Returns Trending List
@param data{object}: card data
@returns data{string},type{int}: Trending HTML
*/
function getTrendingHtml(data,type){
	return '<div class="trending"><div class="trending-title"><h4 class="title-deco title-deco--sm">'+type+'</h4></div><div class="white-space space-mini"></div><div class="trending-list row">'+data+'</div><div class="white-space space-mini"></div><a href="/explore?p='+type+'" class="no-shadow waves-effect waves-light btn red trending-more">More</a></div>';
}

/*
 Loads Ajax Result
 @param searchInput{string} Search keyword or playlist to fetch,resType{int} Search Type
*/
function loadResult(searchInput,resType){

	$('#search-preloader').show();
	$('#result-keyword').hide();

	/*Result Type
	0:For Search
	1:for PlayList*/
	var resAPI = ['/api/v1/search?q=','/api/v1/trending?number=40&type='];

	resType = typeof resType !=='undefined'?resType:0;

	$('#search-result').html('');

	$.getJSON(resAPI[resType] + searchInput, success=function(data, textStatus, jqXHR){
		var dataResult = data['results'];
		//var searchKeyword = data['metadata']['q'];

		if(!dataResult.length && resType == 0) {
			$('#result-keyword h4').html('No results found');
			$('#result-keyword').show();
			$('#search-preloader').hide();
			return false;
		}

		if(!data["metadata"]["count"] && resType == 1) {
			$('#result-keyword h4').html('No results found');
			$('#result-keyword').show();
			$('#search-preloader').hide();
			return false;
		}

		if(resType === 1) {
			$('#result-keyword h4').html('Showing top results for <span class="color-primary">"'+data['metadata']['type']+'"</span>');
		}
		else
			$('#result-keyword h4').html('Showing results for <span class="color-primary">"'+data['metadata']['q']+'"</span>');

		if(resType == 1) {
			dataResult[data["metadata"]["type"]].forEach(function(res){
				$('#search-result').append(getCardHtml(res));
			});

		} else {
			dataResult.forEach(function(res){
				$('#search-result').append(getCardHtml(res));
			});
		}
		$('#result-keyword').show();
		$('#search-preloader').hide();
	})
}

/*
 Loads Trending Section through Ajax
 @param type{string} trending type {eg.pop,rock},number{int} no. of result
 */
function loadTrending(type,number){
	$.getJSON('/api/v1/trending?type=' + type+'&number='+number, success=function(data, textStatus, jqXHR){
		var dataResult = data['results'];
		var searchKeywords = data['metadata']['type'].split(",");

		searchKeywords.forEach(function (res) {
			var trendingCard = '';
			dataResult[res].forEach(function(res1){
				trendingCard += getCardHtml(res1);
			});
			$('#home-trending').append(getTrendingHtml(trendingCard,res));
		});

	})
}

/*
Loads Trending section on homepage
@param:count{int} number of results to load
*/
function trendingInit(){
	$.getJSON('/api/v1/playlists', success=function(data, textStatus, jqXHR){
		var results = data['results'];
		var type_str = '';
		for (var i = 0;i<data["metadata"]["count"];i++){
			type_str += results[i]["playlist"] + ',';
		}
		type_str = type_str.substring(0, type_str.length - 1);
		loadTrending(type_str, 4);
	})
}

/*
 Loads autocomplete
 @param:{string} the keyword for autocomplete
 */
function loadAutoSuggest(searchInput) {
	//Fetches Auto Suggestion
	$.getJSON("http://suggestqueries.google.com/complete/search?callback=?",
		{
			"hl":"en", // Language
			"ds":"yt", // Restrict lookup to youtube
			"jsonp":"suggestCallBack", // jsonp callback function name
			"q":searchInput, // query term
			"client":"youtube" // force youtube style response, i.e. jsonp
		}
	);

	//Callback on response
	suggestCallBack = function (data) {
		var dataResult = data[1].slice(5),
			resultHtml='';

		if(!dataResult.length) {
			$('.search-suggestions .search-suggestions-res').html('<li><a href="#!">No Suggestion</a></li>');
			return;
		}
		//console.log(dataResult);

		//Appends Reults
		dataResult.forEach(function(res){
			resultHtml+='<li><a href="/explore?q='+res[0].trim()+'">'+res[0]+'</a>';
		});
		//loadResult(dataResult[0][0]);//Loads first item of result
		$('.search-suggestions .search-suggestions-res').html(resultHtml);
	};
}

function startStream(streamPlayer,streamUrl) {
	console.log(streamUrl);
	streamPlayer[0].pause();
	$streamContainer = $('#stream-player-container');
	// $streamModel.openModal();
	$streamContainer.addClass('stream-wait');
	// $('#stream-preloader').show();

	$.getJSON(streamUrl, success=function(data, textStatus, jqXHR){
		$('#stream-player-container').removeClass('stream-wait');
		// $('#stream-preloader').hide();
		if (data['status'] != 200){
			Materialize.toast('<h4 class="font-200">Can\'t Stream</h4>', 4000);
			return;
		}
		console.log(data);
		$('#stream-player').attr('src',data['url']);
		streamPlayer[0].play();
		/*elem.hide();
		elem.siblings('audio').attr('src', data['url']);
		elem.siblings('audio').show();*/
	});
	return false;
}
