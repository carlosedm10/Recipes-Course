# INPUTS
altura = float(input("Dime tu altura en centímetros: "))
print("Dime tu peso en kilogramos:")
assert altura > 0, "La altura debe ser mayor que 0"
peso = float(input())
print("Dime tu edad:")
assert peso > 0, "El peso debe ser mayor que 0"
edad = int(input())
print("Selecciona tu sexo: Hombre (H) o mujer (M)")
sexo = input().upper()
assert sexo in ["H", "M"], "El sexo debe ser H o M"
print("Indica del 1 al 3 tu actividad:")
act = int(input())
assert act in [1, 2, 3], "La actividad debe ser 1, 2 o 3"
print("Selecciona tu objetivo: Definición (D), Volumen (V) o Mantenimiento (M)")
etapa = input().upper()
assert etapa in ["D", "V", "M"], "La etapa debe ser D, V o M"

# ---------------------------------- For men: ----------------------------------------
# Calculating kcal
if sexo == "H":
    kcal_b = 66 + (13.7 * peso + 5 * altura - 6.8 * edad)
    if act == 1:
        kcal = kcal_b * 1.6
    elif act == 2:
        kcal = kcal_b * 1.78
    else:
        kcal = kcal_b * 2.1

    # Calculating Macros
    if etapa == "D":
        kcal = kcal - 200
        prot = 2 * peso
        lip = (kcal * 0.3) / 9
        carb = (kcal - (prot * 4 + lip * 9)) / 4
    elif etapa == "V":
        kcal = kcal + 200
        prot = 1.4 * peso
        lip = (kcal * 0.3) / 9
        carb = (kcal - (prot * 4 + lip * 9)) / 4
    else:
        kcal = kcal
        prot = 1.5 * peso
        lip = (kcal * 0.3) / 9
        carb = (kcal - (prot * 4 + lip * 9)) / 4
# ---------------------------------- For women: ----------------------------------------
# Calculating kcal
if sexo == "M":
    kcal_b = 655 + (9.6 * peso + 1.8 * altura - 4.7 * edad)
    if act == 1:
        kcal = kcal_b * 1.5
    elif act == 2:
        kcal = kcal_b * 1.64
    else:
        kcal = kcal_b * 1.9

    # Ca
    if etapa == "D":
        kcal = kcal - 150
        prot = 2 * peso
        lip = (kcal * 0.3) / 9
        carb = (kcal - (prot * 4 + lip * 9)) / 4
    elif etapa == "V":
        kcal = kcal + 200
        prot = 1.4 * peso
        lip = (kcal * 0.3) / 9
        carb = (kcal - (prot * 4 + lip * 9)) / 4
    else:
        kcal = kcal
        prot = 1.5 * peso
        lip = (kcal * 0.3) / 9
        carb = (kcal - (prot * 4 + lip * 9)) / 4

# ----------------------------OUTPUTS----------------------------------
print(f"Tus calorias ideales son: {str(round(kcal))}kCal")
print(
    f"Tus Macros ideales son: {str(round(prot))}g de proteina, {str(round(carb))}g de carbohidratos, y {str(round(lip))}g de grasas"
)
