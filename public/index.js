//
//Submitted by,
//Arvind Ganesan
//NETID: aganes25@uic.edu
//

$.ajaxSetup({
    headers: {
        'Content-Type': 'application/json'
    }
})
$(document).ready(function() {
  $("#nextButton").addClass('disabled');
})

let paginationCounter = 0
let searchResultsList = []

const resetSelection = () => {
    $('input[name=inlineDefaultRadiosExample]').prop('checked', false);
}
const getResultsForQuery = () => {

    let searchQuery = $('#queryTerm').val()
    if (searchQuery == "") {
        console.log("Enter a search query")
        return
    }
    let selectedRankingAlgorithm = $('input[name=inlineDefaultRadiosExample]:checked').attr('id')
    console.log(selectedRankingAlgorithm)
    if (selectedRankingAlgorithm === undefined) {
        selectedRankingAlgorithm = null
    }
    else
    selectedRankingAlgorithm = selectedRankingAlgorithm.toLowerCase()
    let data = {
        "searchString": searchQuery,
        "rankingAlgorithm": selectedRankingAlgorithm
    }
    $('#overlay').css("display", "block");
    $.post("/processQuery", JSON.stringify(data))
    .done((data) => {
        paginationCounter = 0
        searchResultsList = []
        $('#searchResultsList').html('')
        searchResultsList = JSON.parse(data.replaceAll("'", '"'))
        processData()
    }).fail((error)=> {
        console.error("Error occurred"+error.responseText)

          alert(error.responseText)
          $('#overlay').css("display", "none");
        // Show it in hidden box
    })
}

const processData = () => {
    let topResults = []
    if(searchResultsList.length == 0 ){
        $('#loadingScreen').css("display", "none");
        $("#nextButton").addClass('disabled');

        data = "No relevant results found for the given query. Please refine your query and try again"
        topResults.push(data)
    }
    else if(paginationCounter >= searchResultsList.length) {
        $('#loadingScreen').css("display", "none");
         $("#nextButton").addClass('disabled');
        return
    }
    if(searchResultsList.length > 0 ){
        $("#nextButton").removeClass('disabled');
    }

    if(searchResultsList.length > 0) {
        topResults = searchResultsList.slice(paginationCounter, paginationCounter + 10)
    }
    let listDom = $('#searchResultsList')
    let html = ``

    topResults.forEach((data, index) => {
        html += `<li class="list-group-item"><a href='${data}' target="_blank">${data}</a></li>`
    })
    listDom.append(html)
    paginationCounter += 10
    $('#overlay').css("display", "none");
    console.log(topResults)
}