let form = document.getElementById('registerlinket');
let submitBtn = document.getElementById('submitBtn');
form.addEventListener('submit', (e) =>{
  //submitBtn.setAttribute('disabled','false');
  e.preventDefault();
  //submitBtn.setAttribute('disabled','');
  let data = new FormData(form);

  fetch('./registerlinket', {
    method: 'post',
    body: data
  })
  .then((res)=>res.json())
  .then((json) => {
    console.log(json.status);
    switch (json.status) {
      case 0:
        //error
        break;

      case 1:
        let results = document.getElementById('results');
        results.style.display = 'block';
        document.getElementById('displayLinketSelected').textContent = data.get('linket');
        document.getElementById('confirmData').value = data.get('linket');
        break;

    }
  })
  .catch((err) => console.log(err));

});
