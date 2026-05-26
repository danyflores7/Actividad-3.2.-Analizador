int potencia(int base, int exp) {
    if (exp <= 0) {
        return 1;
    }
    return base * potencia(base, exp - 1);
}

int main() {
    printf(potencia(2, 4));
    return 0;
}
