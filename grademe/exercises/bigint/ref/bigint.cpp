#include "bigint.hpp"

void bigint::trim()
{
	while (digits.size() > 1 && digits[digits.size() - 1] == 0)
		digits.pop_back();
}

unsigned bigint::to_shift() const
{
	unsigned long long r = 0;
	for (size_t i = digits.size(); i-- > 0;)
	{
		r = r * 10 + digits[i];
		if (r > 100000000ULL)
			return 100000000U;
	}
	return (unsigned)r;
}

bigint::bigint() : digits(1, 0) {}

bigint::bigint(unsigned long long n)
{
	do
	{
		digits.push_back((int)(n % 10));
		n /= 10;
	} while (n);
}

bigint::bigint(const bigint &other) : digits(other.digits) {}

bigint &bigint::operator=(const bigint &other)
{
	digits = other.digits;
	return *this;
}

bigint::~bigint() {}

bigint bigint::operator+(const bigint &o) const
{
	bigint r;
	r.digits.clear();
	int carry = 0;
	for (size_t i = 0; i < digits.size() || i < o.digits.size() || carry; i++)
	{
		int s = carry;
		if (i < digits.size())
			s += digits[i];
		if (i < o.digits.size())
			s += o.digits[i];
		r.digits.push_back(s % 10);
		carry = s / 10;
	}
	r.trim();
	return r;
}

bigint &bigint::operator+=(const bigint &o)
{
	*this = *this + o;
	return *this;
}

bigint &bigint::operator++()
{
	return *this += bigint(1);
}

bigint bigint::operator++(int)
{
	bigint tmp(*this);
	*this += bigint(1);
	return tmp;
}

bigint bigint::operator<<(unsigned n) const
{
	bigint r(*this);
	if (r.digits.size() == 1 && r.digits[0] == 0)
		return r;
	r.digits.insert(r.digits.begin(), n, 0);
	return r;
}

bigint bigint::operator>>(unsigned n) const
{
	if (n >= digits.size())
		return bigint();
	bigint r;
	r.digits.assign(digits.begin() + n, digits.end());
	r.trim();
	return r;
}

bigint &bigint::operator<<=(unsigned n) { return *this = *this << n; }
bigint &bigint::operator>>=(unsigned n) { return *this = *this >> n; }
bigint &bigint::operator<<=(const bigint &n) { return *this <<= n.to_shift(); }
bigint &bigint::operator>>=(const bigint &n) { return *this >>= n.to_shift(); }

bool bigint::operator==(const bigint &o) const { return digits == o.digits; }
bool bigint::operator!=(const bigint &o) const { return !(*this == o); }

bool bigint::operator<(const bigint &o) const
{
	if (digits.size() != o.digits.size())
		return digits.size() < o.digits.size();
	for (size_t i = digits.size(); i-- > 0;)
		if (digits[i] != o.digits[i])
			return digits[i] < o.digits[i];
	return false;
}

bool bigint::operator>(const bigint &o) const { return o < *this; }
bool bigint::operator<=(const bigint &o) const { return !(o < *this); }
bool bigint::operator>=(const bigint &o) const { return !(*this < o); }

std::ostream &operator<<(std::ostream &os, const bigint &b)
{
	for (size_t i = b.digits.size(); i-- > 0;)
		os << b.digits[i];
	return os;
}
