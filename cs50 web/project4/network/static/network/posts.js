document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll('button.post-button').forEach(button => {
        button.onclick = function() {
            editPost(this.dataset.post);
        }
    })
    
    document.querySelectorAll('button.heart-button').forEach(button => {
        button.onclick = function() {
            heartPost(this.dataset.post);
        }
    })
    
        
    document.querySelectorAll('button.unheart-button').forEach(button => {
        button.onclick = function() {
            unHeartPost(this.dataset.post);
        }
    })


    
    // by default show all the posts, with no edit windows
    showPosts();

});

function unHeartPost(post_id) {
    post = document.querySelector(`#hc${post_id}`);
    currentHearts = parseInt(String(post.textContent).substring(2)); // removes first two characters (the heart and space)
    fetch(`/post-api/${post_id}`, {
      method: "PUT",
      body: JSON.stringify({
        hearts: currentHearts-1,
      }),
    }).then(() => {
        post.textContent=`👍 ${currentHearts-1}`;
        document.querySelector(`#hb${post_id}`).style.display = 'block';
        document.querySelector(`#uhb${post_id}`).style.display = 'none';

    });
  }  


function heartPost(post_id) {
    post = document.querySelector(`#hc${post_id}`);
    currentHearts = parseInt(String(post.textContent).substring(2)); // removes first two characters (the heart and space)
    fetch(`/post-api/${post_id}`, {
      method: "PUT",
      body: JSON.stringify({
        hearts: currentHearts+1,
      }),
    }).then(() => {
        post.textContent=`👍 ${currentHearts+1}`;
        document.querySelector(`#hb${post_id}`).style.display = 'none';
        document.querySelector(`#uhb${post_id}`).style.display = 'block';

    });
  }  

function showPosts(){

    var post = document.getElementsByClassName('post');
    for (var i = 0; i < post.length; i++ ) {
        post[i].style.display = "block";
    }

    var editPost = document.getElementsByClassName('edit-post');
    for (var i = 0; i < editPost.length; i++ ) {
        editPost[i].style.display = "none";
    }


    var editPost = document.getElementsByClassName('unheart-button');
    for (var i = 0; i < editPost.length; i++ ) {
        editPost[i].style.display = "none";
    }


}

function savePost(post,content){
    fetch(`/post-api/${post.id}`, {
        method: "PUT",
        body: JSON.stringify({
            content: content,
        }),
      }).then(() => {
        document.querySelector(`#pc${post.id}`).textContent=content;
        document.querySelector(`#p${post.id}`).style.display = 'block';
        document.querySelector(`#e${post.id}`).style.display = 'none';

      });
  }

function editPost(post_id){
    fetch(`/post-api/${post_id}`)
    .then((response) => response.json())
    .then((post) => {
        document.querySelector(`#p${post_id}`).style.display = 'none';

        const edit_view = document.querySelector(`#e${post_id}`);
    
        edit_view.style.display = 'block';

        const content = document.createElement('textarea');
        content.innerHTML = post.content;
        content.className="form-control";
        edit_view.append(content);    

        const saveButton = document.createElement("button");
        saveButton.classList.add("save-button");
        saveButton.classList.add("btn-primary");
        saveButton.classList.add("btn");

        saveButton.innerHTML = "Update this post";
        edit_view.append(saveButton);
        saveButton.addEventListener("click", () => savePost(post,content.value));
    
    });
}