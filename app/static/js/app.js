
function init(){
    console.log("in load")
    $('.recipeButton').prop('disabled', true);
    $('.cuisines').prop('disabled', true);
    $('.note').hide();
}


// Add the image
$(".imgAdd").click(function () {
    $(this).closest(".row").find('.imgAdd').before(
                     '<div class="col-lg-3 col-sm-3 imgUp">\
                      <figcaption class="figure-caption" id="image-name" placeholder="Image name here.">Upload to Predict</figcaption>\
                      <br>\
                      <div class="form-group"> \
                      <div class="imagePreview"></div> \
                      <div class="upload-options"> \
                      <label><i class="fas fa-upload"></i><input type="file" name="file" class="image-upload" accept="image/*;capture=camera" /></label> \
                      </div></div> \
                      <i class="fa fa-times del"></i></div>');
});

//Scrol the view when show me how clicked
$("#how").click(function () {
    document.getElementById( 'how' ).scrollIntoView();
});


//dlete the image box
$(document).on("click", "i.del" , function() {
	$(this).parent().remove();
});

/////////////////////////////////////////////////////////////////////////////////
//Upload the image and predict
$(function() {
    $(document).on("change",".image-upload", function(){
        var uploadFile = $(this);
        var files = !!this.files ? this.files : [];
        if (!files.length || !window.FileReader) return; // no file selected, or no FileReader support

        var captions = document.getElementsByClassName("figure-caption");
        //Show message while predicting
        for (i = 0; i < captions.length; i++) {
            captions[i].textContent = "Predicting ... ";
            console.log(captions[i].textContent)
        }

        if (/^image/.test( files[0].type)){ // only image file
            var reader = new FileReader(); // instance of the FileReader
            reader.readAsDataURL(files[0]); // read the local file

            reader.onloadend = function(){ // set image data as background of div
                //alert(uploadFile.closest(".upimage").find('.imagePreview').length);
            uploadFile.closest(".imgUp").find('.imagePreview').css("background-image", "url("+this.result+")");
            var form_data = new FormData();
            $.each($(".image-upload"), function (i, obj) {
                $.each(obj.files, function (j, file) {
                    form_data.append('file', file); // is the var i against the var j, because the i is incremental the j is ever 0
                    console.log(file);
                });
            });

            // form_data.append('file', $('.image-upload').prop('files')[0]);
            // console.log(form_data);

            req = $.ajax({
                url : '/',
                type : 'POST',
                contentType:false,
                processData:false,
                cache: false,
                data : form_data,
                success: function(data) {
                    console.log('------------------------------');
                    console.log(data)

                    let image_ids = document.getElementsByClassName("image-upload");
                    let captions = document.getElementsByClassName("figure-caption");
                    for (i = 0; i < captions.length; i++) {
                        let name = data.predictions[i][1];
                        console.log(name);
                        if (name == ""){
                            captions[i].textContent = "Please try again"
                            $('.recipeButton').prop('disabled', true);
                            $('.cuisines').prop('disabled', true);
                            $('.note').hide();
                        }
                        else{
                            captions[i].textContent = name
                            $('.recipeButton').prop('disabled', false)
                            $('.cuisines').prop('disabled', false);
                            $('.note').show();
                        }
                    }
                },
            });
            }
        }
    });
});

/////////////////////////////////////////////////////////////////////////////////////////////
// Show the recipe when button click
$(document).on("click",".recipeButton", function(){
    console.log('RecipeButton click ');
    $('#products').html('<h6 class="wait"><strong>Please wait ... </strong><h6>')
    var ingredients = []
    let captions = document.getElementsByClassName("figure-caption")
    for (i = 0; i < captions.length; i++) {
        ingredients.push(captions[i].textContent)
    }
    console.log(ingredients);
    var e = document.getElementById("cuisine_dd");
    var cuisine = e.options[e.selectedIndex].value;
    console.log('cuisine');
    console.log(cuisine);

    if(cuisine=='Global'){ //This name is defined in index.html
        edaman_api(ingredients);
    }
    else{
        $('#mainContainer').html('<div class="container" id="mainContainer"><div class="row"><div class="col-md-9"><div id="recipeDisplay" class="col-md-12"></div></div></div></div>')
        req = $.ajax({
            url : '/find_recipe',
            type : 'POST',
            contentType:false,
            processData:false,
            cache: false,
            data: JSON.stringify({'ingredients': ingredients, 'cuisine':cuisine}),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                $("#products").html(data['data'])
                console.log(data['data']);
            },
            error: function(error) {
                edaman_api(ingredients);
                // $("#products").html('<br><br><h4 style="color:red;">'+error.responseText+'</h4>')
                    // '<div class="alert alert-danger alert-dismissible fade show"><button type="button" class="close" data-dismiss="alert">×</button><h4 class="alert-heading">Error!</h4> + error')
                 console.log(error);
            }
        });
    }
});


//////////////////////////////////////////////////////////////////////////////////////////
function edaman_api(items){
   $('#products').html('')
   var url = 'https://api.edamam.com/search?q=' + items + '&app_id=b8fa8ec0&app_key=2e99e135530eaed01cb9620b24c1f1c0&health=vegan';
   function displayRecipes() {
   d3.json(url).then(function(response) {
       // console.log(response.hits[0]["recipe"]["label"])
       var results = response.hits;


       $('#recipeDisplay').html('');
       var recipeTitle = []
       console.log(results[i])
       for (i = 0; i < results.length; i++) {
           console.log(response.hits[0]);
           var recipeImage = $('<img>');
           var recipeDiv = $('<div>');
           var recipeCaption = $('<div>');
           var recipeIngradient = $('<div>');
           var recipeBtnDiv = $('<div>');
           var intCalories = (results[i].recipe.calories)/(results[i].recipe.yield);
           var calories = (Math.floor(intCalories));
           var caloriesP = $('<p>');
           //recipeCaption.addClass('caption');

           //recipeCaption.addClass('text-center');
           recipeCaption.append($('<p>').text(results[i].recipe.label).addClass('recipeName'))
           //recipe Ingradient
           recipeIngradient.append($('<p style="font-weight: bold;">').text("Ingredients").addClass('recipeName'))
           for(j=0; j <results[i].recipe.ingredients.length; j++){
                console.log(results[i].recipe.ingredients[j].text)
               recipeIngradient.append($('<p>').text(results[i].recipe.ingredients[j].text).addClass('recipeName'))
           }
           caloriesP.text(calories + ' Calories');
           recipeCaption.append(caloriesP)
           recipeImage.attr('src', results[i].recipe.image);
           //recipeDiv.addClass('row');
           // recipeDiv.addClass('row');
           recipeDiv.addClass('thumbnail col-md-4 recipe');
           recipeDiv.append(recipeImage);
           recipeDiv.addClass('image-center');
           recipeTitle.push(results[i]["recipe"]["label"])
           // recipeCaption.append($('<div>').text(results[i].recipe.label).addClass('recipeName'));
           recipeCaption.addClass('text-center');
           recipeDiv.append(recipeCaption);

           recipeIngradient.addClass('text-center');
           recipeDiv.append(recipeIngradient);

           recipeBtnDiv.append($('<a>').append($('<button>').addClass('btn recipeBtn').text('Go to recipe')).attr('href',results[i].recipe.url).attr('target','_blank'));
           recipeCaption.append(recipeBtnDiv);
           recipeIngradient.append(recipeBtnDiv);

           $('#recipeDisplay').prepend(recipeDiv);
       }
       console.log(recipeTitle)
       //console.log(recipeCaption)
   })
   .catch(() => {
       $("#products").html('<br><br><h6 style="color:red;">An error has occurred. Try again later</h6>')
      })
   };
   displayRecipes();
}
