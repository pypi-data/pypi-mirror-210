#pragma once

    #include "definitions.cpp"
    #include <algorithm>

    double NA2Angle(const double &NA)
    {
        if (NA <= 1.0)
            return asin(NA);

        if (NA >= 1.0)
            return asin(NA-1.0) + PI/2.0;

        return 1.0;
    }

    template <typename T>
    T Concatenate(T &Vector0, T &Vector1)
    {
        T Output = Vector0;
        Output.insert( Output.end(), Vector0.begin(), Vector0.end() );
        return Output;
    }

    template <typename T>
    T Concatenate(T &Vector0, T &Vector1, T &Vector2)
    {
        T Output = Vector0;
        Output.insert( Output.end(), Vector1.begin(), Vector1.end() );
        Output.insert( Output.end(), Vector2.begin(), Vector2.end() );
        return Output;
    }

    template <class T>
    T Sum(const std::vector<T>& vector)
    {
        const long unsigned int N = vector.size();
        T sum = 0.;
        for (auto v: vector)
            sum += v;

        return sum;
    }

    template <class T>
    T Sum(const std::vector<T>& vector0, const std::vector<T>& vector1)
    {
        const size_t N = vector0.size();
        T sum = 0.;
        for (size_t iter=0; iter<vector0.size(); iter++)
            sum += vector0[iter] * vector1[iter];

        return sum;
    }


    template <class T>
    void Squared(std::vector<T>& vector)
    {
        for (size_t iter=0; iter<vector.size(); iter++)
            vector[iter] = pow(abs(vector[iter]), 2);
    }

    template <class T>
    std::vector<T> Add(std::vector<T>& vector0, std::vector<T>& vector1)
    {
        std::vector<T> Output;
        Output.reserve( vector0.size() );

        for (size_t iter=0; iter<vector0.size(); iter++)
            Output.push_back( vector0[iter] + vector1[iter] );

        return Output;
    }



    void
    Unstructured(uint Sampling, complex128 *array0, complex128 *array1, complex128  scalar, complex128 *output)
    {
        for (size_t p=0; p < Sampling; p++ )
        {
            *output   = scalar * array0[p] * array1[p];
            output++;
        }
    }


    CVector
    Unstructured(CVector &array0, CVector &array1, complex128 &scalar)
    {
        CVector output;
        output.reserve(array1.size());

        for (size_t p=0; p < array1.size(); p++ )
            output.push_back( scalar * array0[p] * array1[p] );

        return output;
    }


    CVector
    Structured_( CVector &STerm, CVector &CosSinTerm, complex128 &scalar)
    {
        CVector output;
        output.reserve(STerm.size() * CosSinTerm.size());

        for (auto S : STerm)
            for (auto Trig : CosSinTerm )
                output.push_back( scalar * S * Trig );

        return output;
    }


    void
    Structured(uint ThetaLength, uint PhiLength, complex128 *array0, complex128 *array1, complex128  scalar, complex128 *output)
    {
        for (uint p=0; p < PhiLength; p++ )
            for (uint t=0; t < ThetaLength; t++ )
            {
                *output   = scalar * array0[p] * array1[t];
                output++;
            }
    }
