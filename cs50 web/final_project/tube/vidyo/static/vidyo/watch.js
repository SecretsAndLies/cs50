document.addEventListener("DOMContentLoaded", function () {

    // by default show all the posts, with no edit windows
    showStars();

});


function showStars() {
    rating = document.querySelector(`.rating`);
    rating.append(redStar());
    rating.append(redStar());
    rating.append(redStar());
    rating.append(blackStar());
    rating.append(blackStar());
}


function redStar() {
    const element = document.createElement("span");
    element.classList = "fa fa-star checked";
    return element;
  }

  function blackStar() {
    const element = document.createElement("span");
    element.classList = "fa fa-star";
    return element;
  }