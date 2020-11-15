// venues delete buttons.
venueDeleteBtns = document.querySelectorAll('.btn-delete-venue');
for (let i = 0; i < venueDeleteBtns.length; i++) {
    // the selected venue button.
    const venueDeleteBtn = venueDeleteBtns[i];
    
    venueDeleteBtn.onclick = (e)=>{
        console.log(e);
    
        // the clicked venue id.
        venueId = e.target.dataset['id'];
        // fetch the delete route.
        fetch(`/venues/${venueId}/delete`, {
            method:'DELETE',
        }).then((res)=>{
            console.log(res);
            if (res.status == 200) {
                window.location.href = '/venues';
            } else {
                // display error if the venue already has shows.
                document.getElementById('js-err-msg').style.display = 'block';
                document.getElementById('js-err-msg').innerText = 'Oops, Please note that a venue with shows couldn\'t be deleted.';
            }
        });
    }
}

// venues edit buttons.
venueEditBtns = document.querySelectorAll('.btn-edit-venue');
for (let i = 0; i < venueEditBtns.length; i++) {
    // the selected venue button.
    const venueEditBtn = venueEditBtns[i];

    venueEditBtn.onclick = (e)=>{
        console.log(e);
        // the clicked venue id.
        venueId = e.target.dataset['id'];
        // redirect to the edit route.
        window.location.href = `/venues/${venueId}/edit`;
    }
}

// artists delete buttons.
artistDeleteBtns = document.querySelectorAll('.btn-delete-artist');
for (let i = 0; i < artistDeleteBtns.length; i++) {
    // the selected artist button.
    const artistDeleteBtn = artistDeleteBtns[i];
    
    artistDeleteBtn.onclick = (e)=>{
        console.log(e);
        
        // the clicked artist id.
        artistId = e.target.dataset['id'];
        // fetch the delete route.
        fetch(`/artists/${artistId}/delete`, {
            method:'DELETE',
        }).then((res)=>{
            console.log(res);
            if (res.status == 200) {
                window.location.href = '/artists';
            } else {
                // display error if the artist already has shows.
                document.getElementById('js-err-msg').style.display = 'block';
                document.getElementById('js-err-msg').innerText = 'Oops, Please note that a artist with shows couldn\'t be deleted.';
            }
        });
    }
}

// artists edit buttons.
artistEditBtns = document.querySelectorAll('.btn-edit-artist');
for (let i = 0; i < artistEditBtns.length; i++) {
    // the selected artist button.
    const artistEditBtn = artistEditBtns[i];

    artistEditBtn.onclick = (e)=>{
        console.log(e);
        // the clicked artist id.
        artistId = e.target.dataset['id'];
        // redirect to the edit route.
        window.location.href = `/artists/${artistId}/edit`;
    }
}