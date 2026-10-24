#include "bigint.hpp"
#include <iostream>

int main()
{
    const bigint a(2147483647);
    bigint b(999999999), c, d(1000000000), e(d);


    std::cout << "a = " << a << std::endl;
    std::cout << "b = " << b << std::endl;
    std::cout << "c = " << c << std::endl;
    std::cout << "d = " << d << std::endl;
    std::cout << "e = " << e << std::endl;
    std::cout << "a + b = " << a + b << std::endl;
    std::cout << "(c += a) = " << (c += a) << std::endl;
    std::cout << "b = " << b << std::endl;
    std::cout << "++b = " << ++b << std::endl;
    std::cout << "b++ = " << b++ << std::endl;
    std::cout << "(b << 30) + 999 = " << (b << 30) + 999 << std::endl;
    std::cout << "(d <<= 25) = " << (d <<= 25) << std::endl;
    std::cout << "(d >>= 30) = " << (d >>= (const bigint)30) << std::endl;
    std::cout << "a = " << a << std::endl;
    std::cout << "d = " << d << std::endl;
    std::cout << "(d < a) = " << (d < a) << std::endl;
    std::cout << "(d > a) = " << (d > a) << std::endl;
    std::cout << "(d == a) = " << (d == a) << std::endl;
    std::cout << "(d != a) = " << (d != a) << std::endl;
    std::cout << "(d <= a) = " << (d <= a) << std::endl;
    std::cout << "(d >= a) = " << (d >= a) << std::endl;

    return (0);
}
