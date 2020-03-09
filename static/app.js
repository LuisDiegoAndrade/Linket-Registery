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
        localStorage.setItem('newlinket', data.get('newlinket'));
        document.getElementById('displayLinketSelected').textContent = data.get('linket');
        let confirmLinket = document.getElementById('confirmData');
        confirmlinket.addEventListener('submit', (e) => {
          let confirmData = new FormData(confirmLinket);
          confirmData.set('newlinket', data.get('newlinket'));
        });
        break;

    }
  })
  .catch((err) => console.log(err));

});
