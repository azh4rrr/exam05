#include "bigint.hpp"
#include <iostream>

int main()
{
	bigint nines;
	for (int i = 0; i < 42; i++)
		nines = (nines << 1) + 9;
	std::cout << "nines = " << nines << std::endl;
	bigint big(nines);
	++big;
	std::cout << "nines + 1 = " << big << std::endl;
	std::cout << "nines + nines = " << nines + nines << std::endl;
	std::cout << "nines + 1 + nines = " << big + nines << std::endl;

	std::cout << "big >> 41 = " << (big >> 41) << std::endl;
	std::cout << "big >> 42 = " << (big >> 42) << std::endl;
	std::cout << "big >> 43 = " << (big >> 43) << std::endl;
	std::cout << "big >> 1000 = " << (big >> 1000) << std::endl;
	std::cout << "nines >> 40 = " << (nines >> 40) << std::endl;
	std::cout << "nines >> 0 = " << (nines >> 0) << std::endl;
	std::cout << "nines << 0 = " << (nines << 0) << std::endl;

	bigint zero;
	const bigint zero2(0);
	std::cout << "zero = " << zero << std::endl;
	std::cout << "zero2 = " << zero2 << std::endl;
	std::cout << "zero << 10 = " << (zero << 10) << std::endl;
	std::cout << "zero2 << 3 = " << (zero2 << 3) << std::endl;
	std::cout << "zero + zero = " << zero + zero << std::endl;
	std::cout << "(zero <<= 5) = " << (zero <<= 5) << std::endl;
	std::cout << "zero + 7 = " << zero + 7 << std::endl;
	std::cout << "(zero == zero2) = " << (zero == zero2) << std::endl;

	bigint ten(10);
	std::cout << "ten >> 1 = " << (ten >> 1) << std::endl;
	std::cout << "ten >> 2 = " << (ten >> 2) << std::endl;
	bigint thousand(1000);
	std::cout << "(thousand >>= 3) = " << (thousand >>= 3) << std::endl;
	std::cout << "(thousand >>= 1) = " << (thousand >>= 1) << std::endl;
	bigint hundred(100100);
	std::cout << "(hundred >>= (const bigint)2) = " << (hundred >>= (const bigint)2) << std::endl;
	std::cout << "(hundred >>= (const bigint)5) = " << (hundred >>= (const bigint)5) << std::endl;

	bigint p(1);
	for (int i = 0; i < 256; i++)
		p += p;
	std::cout << "2^256 = " << p << std::endl;

	bigint f0, f1(1);
	for (int i = 0; i < 400; i++)
	{
		bigint t = f0 + f1;
		f0 = f1;
		f1 = t;
	}
	std::cout << "fib(400) = " << f0 << std::endl;

	bigint s(99);
	std::cout << "s++ = " << s++ << std::endl;
	std::cout << "s = " << s << std::endl;
	std::cout << "++s = " << ++s << std::endl;
	bigint n9(999999999);
	++n9;
	std::cout << "++999999999 = " << n9 << std::endl;
	bigint r(5);
	(r += 5) += 5;
	std::cout << "(r += 5) += 5 -> " << r << std::endl;
	(r <<= 2) <<= 1;
	std::cout << "(r <<= 2) <<= 1 -> " << r << std::endl;
	(r >>= (const bigint)1) >>= (const bigint)1;
	std::cout << "(r >>= 1) >>= 1 -> " << r << std::endl;
	++(++r);
	std::cout << "++(++r) -> " << r << std::endl;

	bigint x = (bigint(123456789) << 20) + 1;
	bigint y = (bigint(123456789) << 20) + 2;
	bigint z = (bigint(123456788) << 20) + 999999;
	bigint w = bigint(1) << 29;
	std::cout << "x = " << x << std::endl;
	std::cout << "y = " << y << std::endl;
	std::cout << "z = " << z << std::endl;
	std::cout << "w = " << w << std::endl;
	const bigint *v[4] = {&x, &y, &z, &w};
	for (int i = 0; i < 4; i++)
		for (int j = 0; j < 4; j++)
			std::cout << i << j << ": "
				<< (*v[i] < *v[j]) << (*v[i] > *v[j])
				<< (*v[i] <= *v[j]) << (*v[i] >= *v[j])
				<< (*v[i] == *v[j]) << (*v[i] != *v[j]) << std::endl;
	std::cout << "(nines < big) = " << (nines < big) << std::endl;
	std::cout << "(big > nines) = " << (big > nines) << std::endl;
	std::cout << "(x == x) = " << (x == x) << std::endl;
	std::cout << "(x <= x) = " << (x <= x) << std::endl;

	const bigint c(1000);
	std::cout << "c + c = " << c + c << std::endl;
	std::cout << "c << 2 = " << (c << 2) << std::endl;
	std::cout << "c >> 2 = " << (c >> 2) << std::endl;
	std::cout << "(c < x) = " << (c < x) << std::endl;
	std::cout << "(c == c) = " << (c == c) << std::endl;
	std::cout << "(c != c) = " << (c != c) << std::endl;
	std::cout << "c = " << c << std::endl;
	return 0;
}
