var stripe = Stripe('pk_test_51HZ4nMFnONXy6XW004Rlc9UGZCQvWRcbv3aOSoiz6iS9D7NOkGAQl1i7fBF9k2BrzMS93c3tUbwvGgb2suazXyDx00ICk3Kxbu');
var elements = stripe.elements();


var style = {
    base: {
        color: "#32325d",
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: "antialiased",
        fontSize: "16px",
        "::placeholder": {
            color: "#aab7c4"
        }
    },
    invalid: {
        color: "#fa755a",
        iconColor: "#fa755a"
    }
};
  

// DISPLAY CARD

var cardElement = elements.create("card", { style: style });
cardElement.mount("#card-element");


// DISPLAY ANY ERRORS ON USER INPUT FOR CARD INFO
cardElement.on('change', function(event) {
var displayError = document.getElementById('card-errors');
if (event.error) {
    displayError.textContent = event.error.message;
} else {
    displayError.textContent = '';
}
});


// SAVE PAYMENT DETAILS TO A PAYMENT METHOD
var form = document.getElementById('subscription-form');


form.addEventListener('submit', function (ev) {
    ev.preventDefault();

    // if previous payment attempted, get latest invocie
    const latestInvoicePaymentIntentStatus = localStorage.getItem(
        'latestInvoicePaymentIntentStatus'
    );

    if (latestInvoicePaymentIntentStatus === 'requires_payment_method') {
        const invoiceId = localstorage.getItem('latestInvoiceId');
        const isPaymentTrue = true;
        // create new payment method and retry payment on invoice with new payment method
        createPaymentMethod({
            card,
            isPaymentRetry,
            invoiceId,
        });
    } else {
        // create a new payment method and create subscription
        createPaymentMethod({ card });
    }
});


function createPaymentMethod({ card, isPaymentRetry, invoiceId }) {
    // Set up payment method for recurring usage
    let billingName = document.querySelector('#name').value;

    stripe.createPaymentMethod(
        {
            type: 'card',
            card: card,
            billin_details: {
                name: billingName,
            },
        }
    )
    .then((result) => {
        if (result.error) {
            displayError(result);
        } else {
            if (isPaymentRetry) {
                // update the payment method and retry invoice payment
                retryInvoiceWIthNewPaymentMethod(
                    {
                        customerId: customerId,
                        paymentMethodId: result.paymentMethod.id,
                        invoiceId: invoiceId,
                        priceId: priceId,
                    }
                );
            } else {
                // create subscription
                createSubscription(
                    {
                        customerId: customerId,
                        paymentMethodId: result.paymentMethod.id,
                        priceId: priceId,
                    }
                );
            }
        }
    });
}

function createSubscription({ customerId, paymentMethodId, priceId }) {
    return (
      fetch('/create-subscription', {
        method: 'post',
        headers: {
          'Content-type': 'application/json',
        },
        body: JSON.stringify({
          customerId: customerId,
          paymentMethodId: paymentMethodId,
          priceId: priceId,
        }),
      })
        .then((response) => {
          return response.json();
        })
        // If the card is declined, display an error to the user.
        .then((result) => {
          if (result.error) {
            // The card had an error when trying to attach it to a customer.
            throw result;
          }
          return result;
        })
        // Normalize the result to contain the object returned by Stripe.
        // Add the additional details we need.
        .then((result) => {
          return {
            paymentMethodId: paymentMethodId,
            priceId: priceId,
            subscription: result,
          };
        })
        .catch((error) => {
          // An error has happened. Display the failure to the user here.
          // We utilize the HTML element we created.
          showCardError(error);
        })
    );
  }