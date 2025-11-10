from varasto import Varasto


def main():
    mehua = Varasto(100.0)
    olutta = Varasto(100.0, 20.2)

    print("Luonnin jälkeen:")
    print(f"Mehuvarasto: {mehua}")
    print(f"Olutvarasto: {olutta}")
    print(f"Olut: saldo={olutta.saldo}, tilavuus={olutta.tilavuus}")

    mehua.lisaa_varastoon(50.7)
    print("Lisätään 50.7")
    print(f"Mehuvarasto: {mehua}")

    print("Virhetilanteita:")
    virhe = Varasto(-100.0)
    print(virhe)

    olutta.lisaa_varastoon(1000.0)
    print("Olut täytetty yli")
    print(f"Olutvarasto: {olutta}")


if __name__ == "__main__":
    main()