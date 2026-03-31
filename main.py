from s3_manager import S3Manager


def mostrar_menu():
    print("\n=== GERENCIADOR AWS S3 COM PYTHON ===")
    print("1 - Enviar JSON dinâmico")
    print("2 - Enviar arquivo local")
    print("3 - Listar arquivos")
    print("4 - Ler JSON da nuvem")
    print("5 - Baixar arquivo")
    print("6 - Deletar arquivo")
    print("0 - Sair")


def main():
    manager = S3Manager()

    while True:
        mostrar_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            nome = input("Nome: ").strip()
            email = input("Email: ").strip()
            mensagem = input("Mensagem: ").strip()

            sucesso, resultado = manager.enviar_json_dinamico(nome, email, mensagem)

            if sucesso:
                print(resultado["mensagem"])
                print(f"Chave S3: {resultado['chave']}")
                print(f"ETag: {resultado['etag']}")
            else:
                print(resultado)

        elif opcao == "2":
            caminho_local = input("Caminho do arquivo local: ").strip()
            chave_s3 = input("Nome/chave no S3 (Enter para manter o nome do arquivo): ").strip()

            if chave_s3 == "":
                chave_s3 = None

            sucesso, resultado = manager.enviar_arquivo_local(caminho_local, chave_s3)
            print(resultado)

        elif opcao == "3":
            prefixo = input("Prefixo/pasta (Enter para listar tudo): ").strip()
            sucesso, resultado = manager.listar_arquivos(prefixo)

            if sucesso:
                if not resultado:
                    print("Nenhum arquivo encontrado.")
                else:
                    for arquivo in resultado:
                        print("-" * 40)
                        print(f"Chave: {arquivo['chave']}")
                        print(f"Tamanho: {arquivo['tamanho_bytes']} bytes")
                        print(f"Última modificação: {arquivo['ultima_modificacao']}")
            else:
                print(resultado)

        elif opcao == "4":
            chave_s3 = input("Digite a chave do JSON no S3: ").strip()
            sucesso, resultado = manager.ler_json_da_nuvem(chave_s3)

            if sucesso:
                print("Conteúdo do JSON:")
                print(resultado)
            else:
                print(resultado)

        elif opcao == "5":
            chave_s3 = input("Digite a chave do arquivo no S3: ").strip()
            caminho_local = input("Digite onde salvar localmente: ").strip()

            sucesso, resultado = manager.baixar_arquivo(chave_s3, caminho_local)
            print(resultado)

        elif opcao == "6":
            chave_s3 = input("Digite a chave do arquivo a deletar: ").strip()
            sucesso, resultado = manager.deletar_arquivo(chave_s3)
            print(resultado)

        elif opcao == "0":
            print("Saindo...")
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()