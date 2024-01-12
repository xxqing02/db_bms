function showModal(modal) {
    modal.style.display = 'block';
}

function hideModal(modal) {
    modal.style.display = 'none';
}

function writeMessage(id, text) {
    const message = document.getElementById(id)
    message.innerHTML = text;
}
function showMessage(id) {
    const messageContainer = document.getElementById(id);
    messageContainer.style.opacity = 1;
    messageContainer.style.display = 'block';

    setTimeout(() => {
        messageContainer.style.opacity = 0;
        messageContainer.style.display = 'none';
    }, 1800);
}

function showSuccessMessage(text) {
    const successId = 'success';
    writeMessage(successId, text);
    showMessage(successId);
}

function showErrorMessage(text) {
    const errorId = 'error';
    writeMessage(errorId, text);
    showMessage(errorId);
}

document.addEventListener("DOMContentLoaded", function() {
    login(); // 登录
    register(); // 注册

    addBook(); // 添加书目
    deleteBook(); // 删除书目
    editBook(); // 编辑书目

    editCopy(); // 编辑书册
    deleteCopy(); // 删除书册
    addCopy(); // 添加书册

    approveBorrow(); // 批准借书
    refuseBorrow(); // 拒绝借书

    borrowBook(); // 借书
    returnBook(); // 还书
});

function login() {
    const loginBtn = document.getElementById('login-btn');
    if (loginBtn === null) {
        return;
    }

    const userType = loginBtn.getAttribute('user-type');
    const form = document.getElementById('login-form');
    form.addEventListener('submit', function(event) { event.preventDefault(); });

    loginBtn.addEventListener('click', () => handleLogin());

    function handleLogin() {
        fetch('/login/' + userType, {
            method: 'POST',
            body: new FormData(form),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status === 'success') {
                window.location.href = data.redirect;
            } else if (data.status === 'error') {
                showErrorMessage(data.error);
            }
        })
        .catch(error => {
            console.error('发生错误:', error);
        });
    }
}

function register() {
    const registerBtn = document.getElementById('register-btn');
    if (registerBtn === null) {
        return;
    }

    const userType = registerBtn.getAttribute('user-type');
    const form = document.getElementById('register-form');
    form.addEventListener('submit', function(event) { event.preventDefault(); });

    registerBtn.addEventListener('click', () => handleRegister());

    function handleRegister() {
        fetch('/register/' + userType, {
            method: 'POST',
            body: new FormData(form),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status === 'success') {
                showSuccessMessage(data.message);
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 2200);
            } else if (data.status === 'error') {
                showErrorMessage(data.error);
            }
        })
        .catch(error => {
            console.error('发生错误:', error);
        });
    }
}



//////////////////////////////////////////////////////////////////////////
// 图书管理员
//////////////////////////////////////////////////////////////////////////

function addBook() {
    const openModalBtn = document.getElementById('open-add-book-modal-btn');
    if (openModalBtn === null) {
        return;
    }

    const modal = document.getElementById('add-book-modal');
    const confirmBtn = document.getElementById('confirm-add-book-btn');
    const cancelBtn = document.getElementById('cancel-add-book-btn');

    const form = document.getElementById('add-book-form');

    openModalBtn.addEventListener('click', () => showModal(modal));
    cancelBtn.addEventListener('click', () => hideModal(modal));
    confirmBtn.addEventListener('click', () => handleAddBook(modal));
    form.addEventListener('submit', function(event) { event.preventDefault(); });

    function handleAddBook() {
        fetch('/librarian/add_book', {
            method: 'POST',
            body: new FormData(form),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status === 'success') {
                hideModal(modal);
                showSuccessMessage(data.message);
                setTimeout(() => {
                    window.location.reload();
                }, 2200);
            } else if (data.status === 'error') {
                showErrorMessage(data.error);
            }
        })
        .catch(error => {
            console.error('发生错误:', error);
        });
    }
}

function deleteBook() {
    const openModalBtns = document.querySelectorAll('.open-delete-book-modal-btn');
    if (openModalBtns === null) {
        return;
    }

    openModalBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const bookId = btn.getAttribute('book-id');
            const modal = document.getElementById('delete-book-modal' + bookId);
            const confirmBtn = document.getElementById('confirm-delete-book-btn' + bookId);
            const cancelBtn = document.getElementById('cancel-delete-book-btn' + bookId);
            const form = document.getElementById('delete-book-form' + bookId);
            form.addEventListener('submit', function(event) { event.preventDefault(); });

            showModal(modal);

            confirmBtn.addEventListener('click', () => handleDeleteBook(modal));
            cancelBtn.addEventListener('click', () => hideModal(modal));

            function handleDeleteBook() {
                fetch('/librarian/delete_book', {
                    method: 'POST',
                    body: new FormData(form),
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    if (data.status === 'success') {
                        showSuccessMessage(data.message);
                        hideModal(modal);
                        setTimeout(() => {
                            window.location.reload();
                        }, 2200);
                    } else if (data.status === 'error') {
                        showErrorMessage(data.error);
                    }
                })
                .catch(error => {
                    console.error('发生错误:', error);
                });
            }
        });
    });
}

function editBook() {
    const openModalBtn = document.getElementById('open-edit-book-modal-btn');
    if (openModalBtn === null) {
        return;
    }

    const modal = document.getElementById('edit-book-modal');
    const confirmBtn = document.getElementById('confirm-edit-book-btn');
    const cancelBtn = document.getElementById('cancel-edit-book-btn');
    const form = document.getElementById('edit-book-form');
    form.addEventListener('submit', function(event) { event.preventDefault(); });

    openModalBtn.addEventListener('click', () => showModal(modal));
    cancelBtn.addEventListener('click', () => hideModal(modal));
    confirmBtn.addEventListener('click', () => handleEditBook(modal));

    function handleEditBook() {
        fetch('/librarian/edit_book', {
            method: 'POST',
            body: new FormData(form),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status === 'success') {
                showSuccessMessage(data.message);
                hideModal(modal);
                setTimeout(() => {
                    window.location.reload();
                }, 2200);
            } else if (data.status === 'error') {
                showErrorMessage(data.error);
            }
        })
        .catch(error => {
            console.error('发生错误:', error);
        });
    }
}

function editCopy() {
    const openModalBtns = document.querySelectorAll('.open-edit-copy-modal-btn');
    if (openModalBtns === null) {
        return;
    }

    openModalBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const copyId = btn.getAttribute('copy-id');
            const modal = document.getElementById('edit-copy-modal' + copyId);
            const confirmBtn = document.getElementById('confirm-edit-copy-btn' + copyId);
            const cancelBtn = document.getElementById('cancel-edit-copy-btn' + copyId);
            const form = document.getElementById('edit-copy-form' + copyId);
            form.addEventListener('submit', function(event) { event.preventDefault(); });

            document.getElementById('edit-position' + copyId).value = btn.getAttribute('position');

            showModal(modal);

            confirmBtn.addEventListener('click', () => handleEditCopy(modal));
            cancelBtn.addEventListener('click', () => hideModal(modal));

            function handleEditCopy() {
                fetch('/librarian/edit_copy', {
                    method: 'POST',
                    body: new FormData(form),
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    if (data.status === 'success') {
                        showSuccessMessage(data.message);
                        hideModal(modal);
                        setTimeout(() => {
                            window.location.reload();
                        }, 2200);
                    } else if (data.status === 'error') {
                        showErrorMessage(data.error);
                    }
                })
                .catch(error => {
                    console.error('发生错误:', error);
                });
            }
        }
    )});
}

function deleteCopy() {
    const openModalBtns = document.querySelectorAll('.open-delete-copy-modal-btn');
    if (openModalBtns === null) {
        return;
    }

    openModalBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const copyId = btn.getAttribute('copy-id');
            const modal = document.getElementById('delete-copy-modal' + copyId);
            const confirmBtn = document.getElementById('confirm-delete-copy-btn' + copyId);
            const cancelBtn = document.getElementById('cancel-delete-copy-btn' + copyId);
            const form = document.getElementById('delete-copy-form' + copyId);
            form.addEventListener('submit', function(event) { event.preventDefault(); });

            showModal(modal);

            confirmBtn.addEventListener('click', () => handleDeleteCopy(modal));
            cancelBtn.addEventListener('click', () => hideModal(modal));

            function handleDeleteCopy() {
                fetch('/librarian/delete_copy', {
                    method: 'POST',
                    body: new FormData(form),
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    if (data.status === 'success') {
                        showSuccessMessage(data.message);
                        hideModal(modal);
                        setTimeout(() => {
                            window.location.reload();
                        }, 2200);
                    } else if (data.status === 'error') {
                        showErrorMessage(data.error);
                    }
                })
                .catch(error => {
                    console.error('发生错误:', error);
                });
            }
        });
    });
}

function addCopy() {
    const openModalBtn = document.getElementById('open-add-copy-modal-btn');
    if (openModalBtn === null) {
        return;
    }

    const modal = document.getElementById('add-copy-modal');
    const confirmBtn = document.getElementById('confirm-add-copy-btn');
    const cancelBtn = document.getElementById('cancel-add-copy-btn');
    const form = document.getElementById('add-copy-form');
    form.addEventListener('submit', function(event) { event.preventDefault(); });

    openModalBtn.addEventListener('click', () => showModal(modal));
    cancelBtn.addEventListener('click', () => hideModal(modal));
    confirmBtn.addEventListener('click', () => handleAddCopy(modal));

    function handleAddCopy() {
        fetch('/librarian/add_copy', {
            method: 'POST',
            body: new FormData(form),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status === 'success') {
                showSuccessMessage(data.message);
                hideModal(modal);
                setTimeout(() => {
                    window.location.reload();
                }, 2200);
            } else if (data.status === 'error') {
                showErrorMessage(data.error);
            }
        })
        .catch(error => {
            console.error('发生错误:', error);
        });
    }
}

function approveBorrow() {
    const approveBtns = document.querySelectorAll('.approve-borrow-btn');
    if (approveBtns === null) {
        return;
    }

    approveBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const borrowId = btn.getAttribute('borrow-id');
            const form = document.getElementById('approve-borrow-form' + borrowId);
            form.addEventListener('submit', function(event) { event.preventDefault(); });

            fetch('/librarian/approve_borrow', {
                method: 'POST',
                body: new FormData(form),
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'success') {
                    window.location.reload();
                } else if (data.status === 'error') {
                    showErrorMessage(data.error);
                }
            })
            .catch(error => {
                console.error('发生错误:', error);
            });
        });
    });
}

function refuseBorrow() {
    const refuseBtns = document.querySelectorAll('.refuse-borrow-btn');
    if (refuseBtns === null) {
        return;
    }

    refuseBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const borrowId = btn.getAttribute('borrow-id');
            const form = document.getElementById('refuse-borrow-form' + borrowId);
            form.addEventListener('submit', function(event) { event.preventDefault(); });

            fetch('/librarian/refuse_borrow', {
                method: 'POST',
                body: new FormData(form),
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'success') {
                    window.location.reload();
                } else if (data.status === 'error') {
                    showErrorMessage(data.error);
                }
            })
            .catch(error => {
                console.error('发生错误:', error);
            });
        });
    });
}

//////////////////////////////////////////////////////////////////////////
// 读者
//////////////////////////////////////////////////////////////////////////

function borrowBook() {
    const borrowBtns = document.querySelectorAll('.borrow-btn');
    if (borrowBtns === null) {
        return;
    }

    borrowBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const copyId = btn.getAttribute('copy-id');
            const form = document.getElementById('borrow-form' + copyId);
            form.addEventListener('submit', function(event) { event.preventDefault(); });

            fetch('/reader/borrow', {
                method: 'POST',
                body: new FormData(form),
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'success') {
                    showSuccessMessage(data.message);
                    setTimeout(() => {
                        window.location.reload();
                    }, 2200);
                } else if (data.status === 'error') {
                    showErrorMessage(data.error);
                }
            })
            .catch(error => {
                console.error('发生错误:', error);
            });
        });
    });
}

function returnBook() {
    const returnBtns = document.querySelectorAll('.return-btn');
    if (returnBtns === null) {
        return;
    }

    returnBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const borrowId = btn.getAttribute('borrow-id');
            const form = document.getElementById('return-form' + borrowId);
            form.addEventListener('submit', function(event) { event.preventDefault(); });

            fetch('/reader/return', {
                method: 'POST',
                body: new FormData(form),
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'success') {
                    showSuccessMessage(data.message);
                    setTimeout(() => {
                        window.location.reload();
                    }, 2200);
                } else if (data.status === 'error') {
                    showErrorMessage(data.error);
                }
            })
            .catch(error => {
                console.error('发生错误:', error);
            });
        });
    });
}