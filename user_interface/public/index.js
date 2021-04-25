$.ajaxSetup({
    headers: {
        'Content-Type': 'application/json'
    }
})

const getResultsForQuery = () => {
    let searchQuery = $('#queryTerm').val()
    let data = {
        "searchString": searchQuery,
    }
    $.post("/processQuery", JSON.stringify(data))
    .done((data) => {
        console.log(data)
    }).fail((error)=> {
        console.error(error)
    })
}