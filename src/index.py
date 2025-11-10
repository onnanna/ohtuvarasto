from varasto import Varasto

def main():

    mehua, olutta = Varasto(100.0), Varasto(100.0, 20.2)
    print(f"Luonnin jälkeen:\nMehuvarasto: {mehua}\n"
          f"Olutvarasto: {olutta}\n"
          f"Olut: saldo = {olutta.saldo}, tilavuus = {olutta.tilavuus}"
        )
    mehua.lisaa_varastoon(50.7)
    print(f"Lisätään 50.7\nMehuvarasto: {mehua}")
    print("Virhetilanteita:")
    print(Varasto(-100.0))
    olutta.lisaa_varastoon(1000.0)
    print(f"Olut täytetty yli\nOlutvarasto: {olutta}")

if __name__ == "__main__":
    main()
