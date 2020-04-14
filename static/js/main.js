var input = document.querySelector('input[name=test]');

var settings = {
    dropdown: {
        enabled: 0
    },
    whitelist: [1111, 222, 333, 444]
}

var tagify = new Tagify(input, settings);