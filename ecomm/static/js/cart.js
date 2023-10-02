console.log('hello cart')
var updateBtns = document.getElementsByClassName('update-cart')
// this returns a query set and we need to loop through it and add event listener for each button of type click
// on each click function will get executed
// this in js is same as self in python
console.log(updateBtns)
console.log(updateBtns[0])

for (var i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){
		var productId = this.dataset.product
		var action = this.dataset.action
		console.log('productId:', productId, 'action:', action)

        console.log('user:', user)
        if (user == 'AnonymousUser'){
            console.log('user is not logged in')
        }
        else{
            // console.log('user is logged in, sending data...')
            updateUserOrder(productId, action)
        }
    })
}

function updateUserOrder(productId, action){
    console.log('user is logged in, sending data...')

    // this is the url where you are going to send post data to the backend
    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            'productId': productId,
            'action': action
        })
        // fetch api is used to send data as a string from frontend to the backend (view function)
    })

    .then((response) => {
        return response.json()
    })

    .then((data) => {
        console.log('data:', data) // data coming from backend (view function - JsonResponse()) to the frontend
        location.reload()
    })
}

// as we are using post call inside js, we need to send csrf token using ajax (code is added in main.html)
// https://docs.djangoproject.com/en/4.2/howto/csrf/