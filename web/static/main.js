$(document).ready(function () {
  $('.cpf').mask('000.000.000-00');
  $('.rg').mask('00.000.000-0');
  $('.telefone').mask('(00) 00000-0000');
  $('.cep').mask('00000-000');

  // Avançar com Enter
  $('form input, form select').on('keydown', function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      const inputs = $(this).closest('form').find('input,select,textarea,button');
      const index = inputs.index(this);
      if (index !== -1 && index + 1 < inputs.length) {
        inputs[index + 1].focus();
      }
    }
  });

  // Buscar endereço via CEP
  $('#cep').on('blur', function () {
    let cep = $(this).val().replace(/\D/g, '');
    if (cep.length === 8) {
      $.getJSON(`https://viacep.com.br/ws/${cep}/json/`, function (dados) {
        if (!("erro" in dados)) {
          $('#endereco').val(dados.logradouro);
          $('#bairro').val(dados.bairro);
          $('#cidade').val(dados.localidade);
          $('#estado').val(dados.uf);
        }
      });
    }
  });
});

function confirmarCadastro() {
  return confirm("Deseja realmente cadastrar este registro?");
}

function confirmarEdicao() {
  return confirm("Deseja salvar as alterações?");
}

function confirmarExclusao() {
  return confirm("Tem certeza que deseja excluir?");
}
