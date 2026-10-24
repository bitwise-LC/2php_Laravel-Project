CREATE DATABASE IF NOT EXISTS prazo_certo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE prazo_certo;

CREATE TABLE IF NOT EXISTS empresas (
    id_empresa INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    endereco_sede VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS empresa_telefones (
    id_telefone INT AUTO_INCREMENT PRIMARY KEY,
    id_empresa INT NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    CONSTRAINT fk_empresa_telefone
      FOREIGN KEY (id_empresa) REFERENCES empresas(id_empresa) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS lojas (
    id_loja INT AUTO_INCREMENT PRIMARY KEY,
    id_empresa INT NOT NULL,
    n_funcionarios INT NOT NULL DEFAULT 0,
    endereco VARCHAR(255) NOT NULL,
    CONSTRAINT ck_loja_funcionarios CHECK (n_funcionarios >= 0),
    CONSTRAINT fk_loja_empresa
      FOREIGN KEY (id_empresa) REFERENCES empresas(id_empresa)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS funcionarios (
    n_funcionario INT AUTO_INCREMENT PRIMARY KEY,
    id_loja INT NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    nome_completo VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    cargo VARCHAR(80) NOT NULL,
    endereco VARCHAR(255) NOT NULL,
    CONSTRAINT fk_funcionario_loja
      FOREIGN KEY (id_loja) REFERENCES lojas(id_loja)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS funcionario_telefones (
    id_telefone INT AUTO_INCREMENT PRIMARY KEY,
    n_funcionario INT NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    CONSTRAINT fk_funcionario_telefone
      FOREIGN KEY (n_funcionario) REFERENCES funcionarios(n_funcionario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    n_funcionario INT NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_funcionario
      FOREIGN KEY (n_funcionario) REFERENCES funcionarios(n_funcionario) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estoques (
    id_estoque INT AUTO_INCREMENT PRIMARY KEY,
    id_loja INT NOT NULL,
    nome VARCHAR(80) NOT NULL DEFAULT 'Estoque principal',
    CONSTRAINT fk_estoque_loja
      FOREIGN KEY (id_loja) REFERENCES lojas(id_loja) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS lotes (
    n_lote INT AUTO_INCREMENT PRIMARY KEY,
    id_estoque INT NOT NULL,
    data_fabricacao DATE NOT NULL,
    validade DATE NOT NULL,
    quantia_produtos INT NOT NULL DEFAULT 0,
    CONSTRAINT ck_lote_datas CHECK (validade >= data_fabricacao),
    CONSTRAINT ck_lote_quantidade CHECK (quantia_produtos >= 0),
    CONSTRAINT fk_lote_estoque
      FOREIGN KEY (id_estoque) REFERENCES estoques(id_estoque) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE,
    descricao VARCHAR(255) NOT NULL DEFAULT ''
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS produtos (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    n_lote INT NOT NULL,
    codigo_produto VARCHAR(60) NOT NULL UNIQUE,
    nome VARCHAR(120) NOT NULL,
    descricao VARCHAR(255) NOT NULL DEFAULT '',
    valor_unitario DECIMAL(10,2) NOT NULL DEFAULT 0,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    CONSTRAINT ck_produto_valor CHECK (valor_unitario >= 0),
    CONSTRAINT ck_produto_quantidade CHECK (quantidade_estoque >= 0),
    CONSTRAINT fk_produto_lote
      FOREIGN KEY (n_lote) REFERENCES lotes(n_lote) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS produto_categorias (
    id_produto INT NOT NULL,
    id_categoria INT NOT NULL,
    PRIMARY KEY (id_produto, id_categoria),
    CONSTRAINT fk_produto_categoria_produto
      FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE CASCADE,
    CONSTRAINT fk_produto_categoria_categoria
      FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS vendas (
    id_venda INT AUTO_INCREMENT PRIMARY KEY,
    id_loja INT NOT NULL,
    data_venda DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valor_venda DECIMAL(12,2) NOT NULL DEFAULT 0,
    tipo_saida ENUM('vendido', 'perdido') NOT NULL DEFAULT 'vendido',
    CONSTRAINT ck_venda_valor CHECK (valor_venda >= 0),
    CONSTRAINT fk_venda_loja
      FOREIGN KEY (id_loja) REFERENCES lojas(id_loja)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS venda_itens (
    id_item INT AUTO_INCREMENT PRIMARY KEY,
    id_venda INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT NOT NULL,
    valor_unitario DECIMAL(10,2) NOT NULL,
    CONSTRAINT ck_item_quantidade CHECK (quantidade > 0),
    CONSTRAINT fk_item_venda
      FOREIGN KEY (id_venda) REFERENCES vendas(id_venda) ON DELETE CASCADE,
    CONSTRAINT fk_item_produto
      FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
) ENGINE=InnoDB;

INSERT INTO categorias (nome, descricao) VALUES
  ('Alimentos', 'Produtos alimentícios'),
  ('Bebidas', 'Bebidas em geral'),
  ('Limpeza', 'Produtos de limpeza'),
  ('Higiene', 'Produtos de higiene'),
  ('Outros', 'Demais produtos')
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao);

DROP PROCEDURE IF EXISTS sp_produtos_proximos_vencimento;
DELIMITER //
CREATE PROCEDURE sp_produtos_proximos_vencimento(
    IN p_id_loja INT,
    IN p_dias INT
)
BEGIN
    SELECT
        p.id_produto,
        p.n_lote,
        p.codigo_produto,
        p.nome,
        p.descricao,
        p.valor_unitario,
        p.quantidade_estoque,
        l.validade,
        l.data_fabricacao
    FROM produtos p
    INNER JOIN lotes l ON l.n_lote = p.n_lote
    INNER JOIN estoques e ON e.id_estoque = l.id_estoque
    WHERE e.id_loja = p_id_loja
      AND p.quantidade_estoque > 0
      AND l.validade BETWEEN CURRENT_DATE() AND DATE_ADD(CURRENT_DATE(), INTERVAL p_dias DAY)
    ORDER BY l.validade ASC, p.nome ASC;
END //
DELIMITER ;
