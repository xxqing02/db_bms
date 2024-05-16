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


document.addEventListener("DOMContentLoaded", function () {
    login(); // 登录
    register(); // 注册

    addBook(); // 添加书目
    deleteBook(); // 删除书目
    editBook(); // 编辑书目

    editCopy(); // 编辑书册
    deleteCopy(); // 删除书册
    addCopy(); // 添加书册

    borrowBook(); // 借书
    // renewalBook(); // 续借
    returnBook(); // 还书
    takeReservedBook(); // 领取预约书籍

    reserveBook(); // 预约
    cancelReservation(); // 取消预约
    payFine(); // 缴纳罚金 
});

function login() {
    const loginBtn = document.getElementById('login-btn');
    if (loginBtn === null) {
        return;
    }

    const userType = loginBtn.getAttribute('user-type');
    const form = document.getElementById('login-form');
    form.addEventListener('submit', function (event) { event.preventDefault(); });

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
    form.addEventListener('submit', function (event) { event.preventDefault(); });

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
    confirmBtn.addEventListener('click', () => handleAddBook());
    form.addEventListener('submit', function (event) { event.preventDefault(); });

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

    openModalBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const bookId = btn.getAttribute('book-id');
            const modal = document.getElementById('delete-book-modal' + bookId);
            const confirmBtn = document.getElementById('confirm-delete-book-btn' + bookId);
            const cancelBtn = document.getElementById('cancel-delete-book-btn' + bookId);
            const form = document.getElementById('delete-book-form' + bookId);
            form.addEventListener('submit', function (event) { event.preventDefault(); });

            showModal(modal);

            confirmBtn.addEventListener('click', () => handleDeleteBook());
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

function payFine() {
    const payBtn = document.getElementById('pay-btn');
    if (payBtn === null) {
        return;
    }

    payBtn.addEventListener('click', function () {
        const form = document.getElementById('pay-form');
        form.addEventListener('submit', function (event) { event.preventDefault(); });

        fetch('/reader/pay_fine', {
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
                } 
            })
            .catch(error => {
                console.error('发生错误:', error);
            });
    });
}

// function renewalBook() {
//     const renewalBtns = document.querySelectorAll('.renewal-btn');
//     if (renewalBtns === null) {
//         return;
//     }

//     renewalBtns.forEach(function (btn) {
//         btn.addEventListener('click', function () {
//             // const borrowId = btn.getAttribute('borrow-id');
//             const iId = btn.getAttribute('i-id');
//             const form = document.getElementById('renewal-form'+iId);
//             form.addEventListener('submit', function (event) { event.preventDefault(); });

//             fetch('/reader/renewal', {
//                 method: 'POST',
//                 body: new FormData(form),
//             })
//                 .then(response => response.json())
//                 .then(data => {
//                     console.log(data);
//                     if (data.status === 'success') {
//                         showSuccessMessage(data.message);
//                         setTimeout(() => {
//                             window.location.reload();
//                         }, 2200);
//                     } 
//                 })
//                 .catch(error => {
//                     console.error('发生错误:', error);
//                 });
//         });
//     })

// }

function editBook() {
    const openModalBtn = document.getElementById('open-edit-book-modal-btn');
    if (openModalBtn === null) {
        return;
    }

    const modal = document.getElementById('edit-book-modal');
    const confirmBtn = document.getElementById('confirm-edit-book-btn');
    const cancelBtn = document.getElementById('cancel-edit-book-btn');
    const form = document.getElementById('edit-book-form');
    form.addEventListener('submit', function (event) { event.preventDefault(); });

    openModalBtn.addEventListener('click', () => showModal(modal));
    cancelBtn.addEventListener('click', () => hideModal(modal));
    confirmBtn.addEventListener('click', () => handleEditBook());

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

function borrowBook() {
    const openModalBtns = document.querySelectorAll('.open-borrow-modal-btn');
    if (openModalBtns === null) {
        return;
    }

    openModalBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const copyId = btn.getAttribute('copy-id');
            const modal = document.getElementById('borrow-modal' + copyId);
            const confirmBtn = document.getElementById('confirm-borrow-btn' + copyId);
            const cancelBtn = document.getElementById('cancel-borrow-btn' + copyId);
            const form = document.getElementById('borrow-form' + copyId);
            form.addEventListener('submit', function (event) { event.preventDefault(); });

            showModal(modal);

            cancelBtn.addEventListener('click', () => hideModal(modal));
            confirmBtn.addEventListener('click', () => handleBorrow());

            function handleBorrow() {
                fetch('/librarian/borrow', {
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

function editCopy() {
    const openModalBtns = document.querySelectorAll('.open-edit-copy-modal-btn');
    if (openModalBtns === null) {
        return;
    }

    openModalBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const copyId = btn.getAttribute('copy-id');
            const modal = document.getElementById('edit-copy-modal' + copyId);
            const confirmBtn = document.getElementById('confirm-edit-copy-btn' + copyId);
            const cancelBtn = document.getElementById('cancel-edit-copy-btn' + copyId);
            const form = document.getElementById('edit-copy-form' + copyId);
            form.addEventListener('submit', function (event) { event.preventDefault(); });

            document.getElementById('edit-position' + copyId).value = btn.getAttribute('position');

            showModal(modal);

            confirmBtn.addEventListener('click', () => handleEditCopy());
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
        )
    });
}

function deleteCopy() {
    const openModalBtns = document.querySelectorAll('.open-delete-copy-modal-btn');
    if (openModalBtns === null) {
        return;
    }

    openModalBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const copyId = btn.getAttribute('copy-id');
            const modal = document.getElementById('delete-copy-modal' + copyId);
            const confirmBtn = document.getElementById('confirm-delete-copy-btn' + copyId);
            const cancelBtn = document.getElementById('cancel-delete-copy-btn' + copyId);
            const form = document.getElementById('delete-copy-form' + copyId);
            form.addEventListener('submit', function (event) { event.preventDefault(); });

            showModal(modal);

            confirmBtn.addEventListener('click', () => handleDeleteCopy());
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
    form.addEventListener('submit', function (event) { event.preventDefault(); });

    openModalBtn.addEventListener('click', () => showModal(modal));
    cancelBtn.addEventListener('click', () => hideModal(modal));
    confirmBtn.addEventListener('click', () => handleAddCopy());

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

function returnBook() {
    const returnBtns = document.querySelectorAll('.return-btn');
    if (returnBtns === null) {
        return;
    }

    returnBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const borrowId = btn.getAttribute('borrow-id');
            const form = document.getElementById('return-form' + borrowId);
            form.addEventListener('submit', function (event) { event.preventDefault(); });

            fetch('/librarian/return', {
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
    })
}

function takeReservedBook() {
    const takeBtns = document.querySelectorAll('.take-reserved-book-btn');
    if (takeBtns === null) {
        return;
    }

    takeBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const reserveId = btn.getAttribute('reserve-id');
            const form = document.getElementById('take-reserved-book-form' + reserveId);
            form.addEventListener('submit', function (event) { event.preventDefault(); });

            fetch('/librarian/take_reserved_book', {
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
    })
}

//////////////////////////////////////////////////////////////////////////
// 读者
//////////////////////////////////////////////////////////////////////////

function reserveBook() {
    const reserveBtn = document.getElementById('reserve-btn');
    if (reserveBtn === null) {
        return;
    }

    const form = document.getElementById('reserve-form');
    form.addEventListener('submit', function (event) { event.preventDefault(); });

    reserveBtn.addEventListener('click', () => handleReservation());

    function handleReservation() {
        fetch('/reader/reserve', {
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
    }
}

function cancelReservation() {
    const openModalBtns = document.querySelectorAll('.open-cancel-reserve-modal-btn');
    if (openModalBtns === null) {
        return;
    }

    openModalBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const reserveId = btn.getAttribute('record-id');
            const modal = document.getElementById('cancel-reserve-modal' + reserveId);
            const confirmBtn = document.getElementById('confirm-cancel-reserve-btn' + reserveId);
            const cancelBtn = document.getElementById('cancel-cancel-reserve-btn' + reserveId);
            const form = document.getElementById('cancel-reserve-form' + reserveId);
            form.addEventListener('submit', function (event) { event.preventDefault(); });

            showModal(modal);

            confirmBtn.addEventListener('click', () => handleCancelReservation());
            cancelBtn.addEventListener('click', () => hideModal(modal));

            function handleCancelReservation() {
                fetch('/reader/cancel_reservation', {
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