/// file taken from:
/// 	https://www.geeksforgeeks.org/header-files-in-c-c-with-examples/

// C++ program to demonstrate the inclusion of header file.

#include <cmath> // Including the standard header file for math operations
#include <iostream>
/// end of includes
using namespace std;

int main()
{
    // Using functions from the included header file
    // (<cmath>)
    int sqrt_res = sqrt(25);
    int pow_res = pow(2, 3);

    // Displaying the results
    cout << "Square root of 25 is: " << sqrt_res << endl;
    cout << "2^3 (2 raised to the power of 3) is: "
         << pow_res << endl;

    return 0;
}
