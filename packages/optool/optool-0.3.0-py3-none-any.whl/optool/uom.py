from typing import Optional

import pint
import pint_pandas

UNITS = pint.get_application_registry()  # See for why this is a good idea https://stackoverflow.com/a/68089489
UNITS.define('square_meter = meter**2 = m² = m2')
UNITS.define('cubic_meter = meter**3 = m3')

# Exchange rates as of May 10, 2022, 3:48 p.m., taken from https://finance.yahoo.com/currency-converter/
UNITS.define('USD = [currency] = $ = usd')
UNITS.define('CHF = USD / 0.9918 = _ = chf')
UNITS.define('EUR = USD / 0.9484 = € = eur')

Quantity = UNITS.Quantity  # Should use this registry, see https://github.com/hgrecco/pint/issues/1480
pint_pandas.PintType.ureg = UNITS


class PhysicalDimension:
    dimensionality: Optional[str] = None


class Absement(PhysicalDimension):
    """
    A measure of sustained displacement of an object from its initial position, i.e. a measure of how far away and
    for how long. In SI units, it is usually measured in meter-seconds (m·s).

    See Also:
        `Wikipedia: Absement <https://en.wikipedia.org/wiki/Absement>`_
    """
    strict = False
    dimensionality = '[length] * [time]'


class Acceleration(PhysicalDimension):
    """
    Rate of change of the velocity of an object with respect to time. In SI units, it is usually measured in meters
    per square seconds (m/s²).

    See Also:
        `Wikipedia: Acceleration <https://en.wikipedia.org/wiki/Acceleration>`_
    """
    strict = False
    dimensionality = '[acceleration]'


class Action(PhysicalDimension):
    """
    Energy multiplied by a duration, used to describe how a physical system has changed over time.

    See Also:
        `Wikipedia: Action (physics) <https://en.wikipedia.org/wiki/Action_(physics)>`_
    """
    strict = False
    dimensionality = '[energy] * [time]'


class AmountOfSubstance(PhysicalDimension):
    """
    Number of elementary entities of a substance. It is one of the seven fundamental physical quantities in both the
    International System of Units (SI) and the International System of Quantities (ISQ). The SI base unit of time is
    the mole (mol).

    One mole contains exactly 6.022 140 76 × 10²³ elementary entities. This number is the fixed numerical value of
    the Avogadro constant, NA, when expressed in the unit 1/mol and is called the Avogadro number.

    See Also:
        `Wikipedia: Amount of substance <https://en.wikipedia.org/wiki/Amount_of_substance>`_
    """
    strict = False
    dimensionality = '[substance]'


class Angle(PhysicalDimension):
    """
    A dimensionless measure describing the relative position of two beams to each other.

    See Also:
        `Wikipedia: Angle <https://en.wikipedia.org/wiki/Angle>`_
    """
    strict = False
    dimensionality = '[]'


class AngularAcceleration(PhysicalDimension):
    """
    The time rate of change of angular velocity. In SI units, it is usually measured in radians per square second
    (rad/s²).

    See Also:
        `Wikipedia: Angular acceleration <https://en.wikipedia.org/wiki/Angular_acceleration>`_
    """
    strict = False
    dimensionality = '[] / [time] ** 2'


class AngularVelocity(PhysicalDimension):
    """
    A measure of how fast the angular position or orientation of an object changes with time. In SI units, it is
    usually measured in radians per second (rad/s).

    See Also:
        `Wikipedia: Angular velocity <https://en.wikipedia.org/wiki/Angular_velocity>`_
    """
    strict = False
    dimensionality = '[] / [time]'


class Area(PhysicalDimension):
    """
    Measure of a region's size on a surface. In SI units, it is usually measured in square meters (m²).

    See Also:
        `Wikipedia: Area <https://en.wikipedia.org/wiki/Area>`_
    """
    strict = False
    dimensionality = '[area]'


class AreaDensity(PhysicalDimension):
    """
    Measure of the mass per unit area of a two-dimensional object. In SI units, it is usually measured in kilograms
    per square meters (kg/m²).

    See Also:
        `Wikipedia: Area density <https://en.wikipedia.org/wiki/Area_density>`_
    """
    strict = False
    dimensionality = '[mass] / [area]'


class CatalyticActivity(PhysicalDimension):
    """
    Measure for quantifying the catalytic activity of enzymes and other catalysts. The SI derived unit for measuring
    the catalytic activity of a catalyst is the katal, which is quantified in moles per second (mol/s).

    See Also:
        `Wikipedia: Catalysis <https://en.wikipedia.org/wiki/Catalysis>`_
    """
    strict = False
    dimensionality = '[activity]'


class Concentration(PhysicalDimension):
    """
    Measure of the concentration of a chemical species in terms of amount of substance per unit volume of solution.
    In SI units, it is usually measured in moles per liter (mol/l).

    See Also:
        `Wikipedia: Molar concentration <https://en.wikipedia.org/wiki/Molar_concentration>`_
    """
    strict = False
    dimensionality = '[concentration]'


class Density(PhysicalDimension):
    """
    Measure of a substance's mass per unit of volume. In SI units, it is usually measured in kilograms per cubic
    meters (kg/m3).

    See Also:
        `Wikipedia: Density <https://en.wikipedia.org/wiki/Density>`_
    """
    strict = False
    dimensionality = '[density]'


class Dimensionless(PhysicalDimension):
    """
    A quantity to which no physical dimension is assigned, with a corresponding SI unit of measurement of one.

    See Also:
        `Wikipedia: Dimensionless quantity <https://en.wikipedia.org/wiki/Dimensionless_quantity>`_
    """
    strict = False
    dimensionality = '[]'


class ElectricalConductivity(PhysicalDimension):
    """
    A measure of a material's ability to conduct electric current. Electrical conductivity is also called specific
    conductance and is the reciprocal of :py:class:`optool.fields.quantities.ElectricalResistivity`. In SI units, it
    is usually measured in siemens per metre (S/m).

    See Also:
        `Wikipedia: Electrical resistivity and conductivity
        <https://en.wikipedia.org/wiki/Electrical_resistivity_and_conductivity>`_
    """
    strict = False
    dimensionality = '[conductance] / [length]'


class ElectricalResistivity(PhysicalDimension):
    """
    A measure of how strongly a material resists electric current. Electrical resistivity is also called specific
    electrical resistance or volume resistivity. In SI units, it is usually measured in ohm-meters (Ω⋅m).

    See Also:
        `Wikipedia: Electrical resistivity and conductivity
        <https://en.wikipedia.org/wiki/Electrical_resistivity_and_conductivity>`_
    """
    strict = False
    dimensionality = '[resistivity]'


class ElectricCapacitance(PhysicalDimension):
    """
    The capability of a material object or device to store electric charge, measured by the change in charge in
    response to a difference in electric potential. The unit commonly used in the SI unit system is the farad (F).

    See Also:
        `Wikipedia: Capacitance <https://en.wikipedia.org/wiki/Capacitance>`_
    """
    strict = False
    dimensionality = '[capacitance]'


class ElectricCharge(PhysicalDimension):
    """
    The physical property of matter that causes charged matter to experience a force when placed in an
    electromagnetic field. The units commonly used in the SI unit system are the coulomb (C) and the ampere-hours
    (A·h).

    See Also:
        `Wikipedia: Electric charge <https://en.wikipedia.org/wiki/Electric_charge>`_
    """
    strict = False
    dimensionality = '[charge]'


class ElectricConductance(PhysicalDimension):
    """
    A measure for the ease with which an electric current passes. Its reciprocal quantity is
    :py:class:`optool.fields.quantities.ElectricalResistance`. The unit commonly used in the SI unit system is the
    siemens (S).

    See Also:
        `Wikipedia: Electrical resistance and conductance
        <https://en.wikipedia.org/wiki/Electrical_resistance_and_conductance>`_
    """
    strict = False
    dimensionality = '[conductance]'


class ElectricCurrent(PhysicalDimension):
    """
    A measure for the net rate of flow of electric charge through a surface or into a control volume. It is one of
    the seven fundamental physical quantities in both the International System of Units (SI) and the International
    System of Quantities (ISQ). The SI base unit of time is the ampere (A).

    See Also:
        `Wikipedia: Electric current <https://en.wikipedia.org/wiki/Electric_current>`_
    """
    strict = False
    dimensionality = '[current]'


class ElectricInductance(PhysicalDimension):
    """
    The ratio of the induced voltage to the rate of change of current causing it. The unit commonly used in the SI
    unit system is the henry (H).

    See Also:
        `Wikipedia: Inductance <https://en.wikipedia.org/wiki/Inductance>`_
    """
    strict = False
    dimensionality = '[inductance]'


class ElectricPermittivity(PhysicalDimension):
    """
    A measure of the electric polarizability of a dielectric. TIn SI units, it is usually measured in farads per
    meter (F/m).

    See Also:
        `Wikipedia: Permittivity <https://en.wikipedia.org/wiki/Permittivity>`_
    """
    strict = False
    dimensionality = '[capacitance] / [length]'


class ElectricPotential(PhysicalDimension):
    """
    A measure for the amount of work energy needed to move a unit of electric charge from a reference point to the
    specific point in an electric field. The unit commonly used in the SI unit system is the volt (V).

    See Also:
        `Wikipedia: Electric potential <https://en.wikipedia.org/wiki/Electric_potential>`_
    """
    strict = False
    dimensionality = '[electric_potential]'


class ElectricResistance(PhysicalDimension):
    """
    A measure for the ease with which an electric current passes. Its reciprocal quantity is
    :py:class:`optool.fields.quantities.ElectricConductance`. The unit commonly used in the SI unit system is the
    ohm (Ω).

    See Also:
        `Wikipedia: Electrical resistance and conductance
        <https://en.wikipedia.org/wiki/Electrical_resistance_and_conductance>`_
    """
    strict = False
    dimensionality = '[resistance]'


class Energy(PhysicalDimension):
    """
    The quantitative property that is transferred to a body or to a physical system, recognizable in the performance
    of work and in the form of heat and light. The unit commonly used in the SI unit system is the joule (J).

    See Also:
        `Wikipedia: Energy <https://en.wikipedia.org/wiki/Energy>`_
    """
    strict = False
    dimensionality = '[energy]'


class Entropy(PhysicalDimension):
    """
    A scientific concept, as well as a measurable physical property, that is most commonly associated with a state
    of disorder, randomness, or uncertainty. It has dimensions of energy divided by temperature. In SI units, it is
    usually measured in joules per kelvin (J/K).

    See Also:
        `Wikipedia: Entropy <https://en.wikipedia.org/wiki/Entropy>`_
    """
    strict = False
    dimensionality = '[entropy]'


class Fluidity(PhysicalDimension):
    """
    The reciprocal of :py:class:`optool.fields.quantities.Viscosity`. In SI units, it is usually reciprocal poise
    (1/P), sometimes called the rhe.

    See Also:
        `Wikipedia: Fluidity <https://en.wikipedia.org/wiki/Fluidity>`_
    """
    strict = False
    dimensionality = '[fluidity]'


class Force(PhysicalDimension):
    """
    An influence that can change the motion of an object. The unit commonly used in the SI unit system is the newton
    (N).

    See Also:
        `Wikipedia: Force <https://en.wikipedia.org/wiki/Force>`_
    """
    strict = False
    dimensionality = '[force]'


class Frequency(PhysicalDimension):
    """
    Number of occurrences of a repeating event per unit of time. The unit commonly used in the SI unit system is the
    hertz (Hz).

    See Also:
        `Wikipedia: Frequency <https://en.wikipedia.org/wiki/Frequency>`_
    """
    strict = False
    dimensionality = '[frequency]'


class Illuminance(PhysicalDimension):
    """
    A measure of how much the incident light illuminates the surface, wavelength-weighted by the luminosity function
    to correlate with human brightness perception. The unit commonly used in the SI unit system is the lux (lx).

    See Also:
        `Wikipedia: Illuminance <https://en.wikipedia.org/wiki/Illuminance>`_
    """
    strict = False
    dimensionality = '[illuminance]'


class Impulse(PhysicalDimension):
    """
    The integral of a force over a time interval for which it acts. In SI units, it is usually measured in newton-
    seconds (N⋅s).

    See Also:
        `Wikipedia: Impulse (physics) <https://en.wikipedia.org/wiki/Impulse_(physics)>`_
    """
    strict = False
    dimensionality = '[length] * [mass] / [time]'


class Information(PhysicalDimension):
    """
    A measure for the capacity of some standard data storage system or communication channel. The unit commonly used
    in the SI unit system is the bit.

    See Also:
        `Wikipedia: Units of information <https://en.wikipedia.org/wiki/Units_of_information>`_
    """
    strict = False
    dimensionality = '[]'


class InformationRate(PhysicalDimension):
    """
    A measure for the speed of data transmission. In SI units, it is usually measured in bits per second (bit/s).

    See Also:
        `Wikipedia: Bit rate <https://en.wikipedia.org/wiki/Bit_rate>`_
    """
    strict = False
    dimensionality = '[frequency]'


class Intensity(PhysicalDimension):
    """
    A measure for the power transferred per unit area, where the area is measured on the plane perpendicular to the
    direction of propagation of the energy. In SI units, it is usually measured in watts per square meter (W/m²).

    See Also:
        `Wikipedia: Intensity (physics) <https://en.wikipedia.org/wiki/Intensity_(physics)>`_
    """
    strict = False
    dimensionality = '[intensity]'


class IonizingRadiation(PhysicalDimension):
    """
    A measure of the energy that is emitted by certain types of atomic nuclei or subatomic particles, such as alpha
    particles, beta particles, and gamma rays. The units commonly used in the SI unit system are the gray (Gy) and
    the sievert (Sv).

    See Also:
        `Wikipedia: Ionizing radiation <https://en.wikipedia.org/wiki/Ionizing_radiation>`_
    """
    strict = False
    dimensionality = '[energy] / [mass]'


class KinematicViscosity(PhysicalDimension):
    """
    A measure of a fluid's resistance to flow. It is defined as the ratio of the dynamic viscosity of a fluid to its
    density. In SI units, it is usually measured in square meters per second (m^2/s).

    See Also:
        `Wikipedia: Viscosity <https://en.wikipedia.org/wiki/Viscosity#Kinematic_viscosity>`_
    """
    strict = False
    dimensionality = '[kinematic_viscosity]'


class Length(PhysicalDimension):
    """
    A measure of distance. It is one of the seven fundamental physical quantities in both the International System
    of Units (SI) and the International System of Quantities (ISQ). The SI base unit of time is the meter (m).

    See Also:
        `Wikipedia: Length <https://en.wikipedia.org/wiki/Length>`_
    """
    strict = False
    dimensionality = '[length]'


class Luminance(PhysicalDimension):
    """
    A photometric measure of the luminous intensity per unit area of light travelling in a given direction. In SI
    units, it is usually measured in candela per square metre (cd/m²).

    See Also:
        `Wikipedia: Luminance <https://en.wikipedia.org/wiki/Luminance>`_
    """
    strict = False
    dimensionality = '[luminance]'


class LuminousFlux(PhysicalDimension):
    """
    A measure of the perceived power of light. The unit commonly used in the SI unit system is the lumen (lm).

    See Also:
        `Wikipedia: Luminous flux <https://en.wikipedia.org/wiki/Luminous_flux>`_
    """
    strict = False
    dimensionality = '[luminous_flux]'


class LuminousIntensity(PhysicalDimension):
    """
    A measure of the wavelength-weighted power emitted by a light source in a particular direction per unit solid
    angle, based on the luminosity function, a standardized model of the sensitivity of the human eye. It is one of
    the seven fundamental physical quantities in both the International System of Units (SI) and the International
    System of Quantities (ISQ). The SI base unit of time is the candela (cd).

    See Also:
        `Wikipedia: Luminous intensity <https://en.wikipedia.org/wiki/Luminous_intensity>`_
    """
    strict = False
    dimensionality = '[luminosity]'


class MagneticFieldStrength(PhysicalDimension):
    """
    A measure of the intensity of a magnetic field. In SI units, it is usually measured in amperes per meter (A/m).

    See Also:
        `Wikipedia: Magnetic field <https://en.wikipedia.org/wiki/Magnetic_field#The_H-field>`_
    """
    strict = False
    dimensionality = '[magnetic_field_strength]'


class MagneticFlux(PhysicalDimension):
    """
    A measure of how many magnetic field lines are passing through a given surface area, that is, a measure of the
    strength of the magnetic field. The unit commonly used in the SI unit system is the weber (Wb).

    See Also:
        `Wikipedia: Magnetic flux <https://en.wikipedia.org/wiki/Magnetic_flux>`_
    """
    strict = False
    dimensionality = '[magnetic_flux]'


class MagneticFluxDensity(PhysicalDimension):
    """
    A measure of the actual magnetic field within a material considered as a concentration of magnetic field lines,
    or flux, per unit cross-sectional area. It is also called the magnitude of the magnetic field. The unit commonly
    used in the SI unit system is the tesla (T).

    See Also:
        `Wikipedia: Magnetic field <https://en.wikipedia.org/wiki/Magnetic_field#The_B-field>`_
    """
    strict = False
    dimensionality = '[magnetic_field]'


class MagneticPermeability(PhysicalDimension):
    """
    A measure of magnetization that a material obtains in response to an applied magnetic field. In SI units, it is
    usually measured in henries per meter (H/m) or equivalently in newtons per ampere squared (N/A²).

    See Also:
        `Wikipedia: Permeability (electromagnetism)
        <https://en.wikipedia.org/wiki/Permeability_(electromagnetism)>`_
    """
    strict = False
    dimensionality = '[inductance] / [length]'


class MagnetomotiveForce(PhysicalDimension):
    """
    The property of certain substances or phenomena that give rise to magnetic fields. The unit commonly used in the
    SI unit system is the ampere (A).

    See Also:
        `Wikipedia: Magnetomotive force <https://en.wikipedia.org/wiki/Magnetomotive_force>`_
    """
    strict = False
    dimensionality = '[magnetomotive_force]'


class Mass(PhysicalDimension):
    """
    One of the seven fundamental physical quantities in both the International System of Units (SI) and the
    International System of Quantities (ISQ). The SI base unit of time is the kilogram (kg).

    See Also:
        `Wikipedia: Mass <https://en.wikipedia.org/wiki/Mass>`_
    """
    strict = False
    dimensionality = '[mass]'


class MassFlowRate(PhysicalDimension):
    """
    A measure of how much mass of a substance passes per unit of time. In SI units, it is usually measured in
    kilograms per second (kg/s).

    See Also:
        `Wikipedia: Mass flow rate <https://en.wikipedia.org/wiki/Mass_flow_rate>`_
    """
    strict = False
    dimensionality = '[mass] / [time]'


class MolarEntropy(PhysicalDimension):
    """
    A measure of entropy per mole. In SI units, it is usually measured in joules per mole per kelvin (J/(mol⋅K)).

    See Also:
        `Wikipedia: Entropy <https://en.wikipedia.org/wiki/Entropy>`_
    """
    strict = False
    dimensionality = '[molar_entropy]'


class MomentOfInertia(PhysicalDimension):
    """
    A measure of how much torque is needed for a desired angular acceleration about a rotational axis, similar to
    how mass determines the force needed for a desired acceleration. It is also known as the rotational inertia. In
    SI units, it is usually measured in kilogram-square meters (kg⋅m²).

    See Also:
        `Wikipedia: Moment of inertia <https://en.wikipedia.org/wiki/Moment_of_inertia>`_
    """
    strict = False
    dimensionality = '[mass] * [length] ** 2'


class Momentum(PhysicalDimension):
    """
    The product of the mass and velocity of an object. In SI units, it is usually measured in kilogram metre per
    second (kg⋅m/s), which is equivalent to the newton-second (N⋅s).

    See Also:
        `Wikipedia: Momentum <https://en.wikipedia.org/wiki/Momentum>`_
    """
    strict = False
    dimensionality = '[momentum]'


class Power(PhysicalDimension):
    """
    The amount of energy transferred or converted per unit time. The unit commonly used in the SI unit system is the
    watt (W).

    See Also:
        `Wikipedia: Power (physics) <https://en.wikipedia.org/wiki/Power_(physics)>`_
    """
    strict = False
    dimensionality = '[power]'


class Pressure(PhysicalDimension):
    """
    The force applied perpendicular to the surface of an object per unit area over which that force is distributed.
    The unit commonly used in the SI unit system is the pascal (Pa).

    See Also:
        `Wikipedia: Pressure <https://en.wikipedia.org/wiki/Pressure>`_
    """
    strict = False
    dimensionality = '[pressure]'


class Radiance(PhysicalDimension):
    """
    A measure of the radiant flux emitted, reflected, transmitted or received by a given surface, per unit solid
    angle per unit projected area. In SI units, it is usually measured in watts per steradian per square metre
    (W/(sr·m²)).

    See Also:
        `Wikipedia: Radiance <https://en.wikipedia.org/wiki/Radiance>`_
    """
    strict = False
    dimensionality = '[power] / [length] ** 2'


class RadiantIntensity(PhysicalDimension):
    """
    A measure of the radiant flux emitted, reflected, transmitted or received, per unit solid angle. In SI units, it
    is usually measured in watts per steradian (W/sr).

    See Also:
        `Wikipedia: Radiant intensity <https://en.wikipedia.org/wiki/Radiant_intensity>`_
    """
    strict = False
    dimensionality = '[power]'


class RadiationDoseAbsorbed(PhysicalDimension):
    """
    A measure for the amount of energy deposited per unit of mass. The unit commonly used in the SI unit system is
    the gray (Gy).

    See Also:
        `Wikipedia: Absorbed dose <https://en.wikipedia.org/wiki/Absorbed_dose>`_
    """
    strict = False
    dimensionality = '[energy] / [mass]'


class RadiationDoseEffective(PhysicalDimension):
    """
    A measure for the effective dose of radiation received by a human or some other living organism. The unit
    commonly used in the SI unit system is the sievert (Sv).

    See Also:
        `Wikipedia: Effective dose (radiation) <https://en.wikipedia.org/wiki/Effective_dose_(radiation)>`_
    """
    strict = False
    dimensionality = '[energy] / [mass]'


class Radioactivity(PhysicalDimension):
    """
    A measure for the activity of a radioactive material in which one nucleus decays per unit of time. The unit
    commonly used in the SI unit system is the becquerel (Bq).

    See Also:
        `Wikipedia: Radioactive decay <https://en.wikipedia.org/wiki/Radioactive_decay>`_
    """
    strict = False
    dimensionality = '[] / [time]'


class SolidAngle(PhysicalDimension):
    """
    A measure of the amount of the field of view from some particular point that a given object covers. The unit
    commonly used in the SI unit system is the steradian (sr).

    See Also:
        `Wikipedia: Radioactive decay <https://en.wikipedia.org/wiki/Radioactive_decay>`_
    """
    strict = False
    dimensionality = '[]'


class SpecificHeatCapacity(PhysicalDimension):
    """
    A measure for the amount of heat energy required to raise the temperature of a substance per unit of mass. In SI
    units, it is usually measured in joules per kelvin per kilogram (J/(kg·K)).

    See Also:
        `Wikipedia: Specific heat capacity <https://en.wikipedia.org/wiki/Specific_heat_capacity>`_
    """
    strict = False
    dimensionality = '[energy] / [mass] / [temperature]'


class Speed(PhysicalDimension):
    """
    The magnitude of the change of an object's position over time or the magnitude of the change of the object's
    position per unit of time. Speed is not the same as :py:class:`optool.fields.quantities.Velocity`, which is a
    vector quantity that has both magnitude and direction. In SI units, it is usually measured in meters per second
    (m/s).

    See Also:
        `Wikipedia: Speed <https://en.wikipedia.org/wiki/Speed>`_
    """
    strict = False
    dimensionality = '[speed]'


class Temperature(PhysicalDimension):
    """
    A physical quantity that expresses quantitatively the perceptions of hotness and coldness. It is one of the
    seven fundamental physical quantities in both the International System of Units (SI) and the International
    System of Quantities. The SI base unit of time is the kelvin (K).

    See Also:
        `Wikipedia: Temperature <https://en.wikipedia.org/wiki/Temperature>`_
    """
    strict = False
    dimensionality = '[temperature]'


class ThermalConductance(PhysicalDimension):
    """
    A measure of how much heat passes in unit time through a plate of particular area and thickness when its
    opposite faces differ in temperature by one kelvin. In SI units, it is usually measured in watts per kelvin
    (W/K).

    See Also:
        `Wikipedia: Thermal conductivity <https://en.wikipedia.org/wiki/Thermal_conductivity>`_
    """
    strict = False
    dimensionality = '[power] / [temperature]'


class ThermalConductivity(PhysicalDimension):
    """
    A measure of a material's ability to conduct heat. In SI units, it is usually measured in watts per meter per
    kelvin (W/(m·K)).

    See Also:
        `Wikipedia: Thermal conductivity <https://en.wikipedia.org/wiki/Thermal_conductivity>`_
    """
    strict = False
    dimensionality = '[power] / ([length] * [temperature])'


class ThermalInsulance(PhysicalDimension):
    """
    A measure of how well a two-dimensional barrier, such as a layer of insulation, a window or a complete wall or
    ceiling, resists the conductive flow of heat. In SI units, it is usually measured in square meter-kelvins per
    watt (K·m²/W).

    See Also:
        `Wikipedia: R-value (insulation) <https://en.wikipedia.org/wiki/R-value_%28insulation%29>`_
    """
    strict = False
    dimensionality = '[temperature] * [length] ** 2 / [power]'


class ThermalResistance(PhysicalDimension):
    """
    The inverse of thermal conductance. It is a convenient measure to use in multi-component design since thermal
    resistances are additive when occurring in series. In SI units, it is usually measured in kelvins per watt
    (K/W).

    See Also:
        `Wikipedia: Thermal conductivity <https://en.wikipedia.org/wiki/Thermal_conductivity>`_
    """
    strict = False
    dimensionality = '[temperature] / [power]'


class ThermalResistivity(PhysicalDimension):
    """
    The reciprocal of :py:class:`optool.fields.quantities.ThermalConductivity`. It is a measure of a material's
    ability to resists the conductive flow of heat. TIn SI units, it is usually measured in kelvin-meters per watt
    (m·K)/W).

    See Also:
        `Wikipedia: Thermal conductivity <https://en.wikipedia.org/wiki/Thermal_conductivity>`_
    """
    strict = False
    dimensionality = '[length] * [temperature] / [power]'


class ThermalTransmittance(PhysicalDimension):
    """
    A measure for the rate of transfer of heat through matter, typically expressed as a U-value. In SI units, it is
    usually measured in watts per square metre per kelvin (W/(m²·K)).

    See Also:
        `Wikipedia: Thermal transmittance <https://en.wikipedia.org/wiki/Thermal_transmittance>`_
    """
    strict = False
    dimensionality = '[power] / ([length] ** 2 * [temperature])'


class Time(PhysicalDimension):
    """
    One of the seven fundamental physical quantities in both the International System of Units (SI) and the
    International System of Quantities (ISQ). The SI base unit of time is the second (s).

    See Also:
        `Wikipedia: Time <https://en.wikipedia.org/wiki/Time>`_
    """
    strict = False
    dimensionality = '[time]'


class Torque(PhysicalDimension):
    """
    The rotational equivalent of linear :py:class:`optool.fields.quantities.Force`. In SI units, it is usually
    measured in newton-meters (N·m).

    See Also:
        `Wikipedia: Torque <https://en.wikipedia.org/wiki/Torque>`_
    """
    strict = False
    dimensionality = '[torque]'


class Velocity(PhysicalDimension):
    """
    The directional speed of an object in motion as an indication of its rate of change in position as observed from
    a particular frame of reference and as measured by a particular standard of time. It is a physical vector
    quantity. Hence, both magnitude and direction are needed to define it. The scalar absolute value (magnitude) of
    velocity is :py:class:`optool.fields.quantities.Speed`. In SI units, it is usually measured in meters per second
    (m/s).

    See Also:
        `Wikipedia: Velocity <https://en.wikipedia.org/wiki/Velocity>`_
    """
    strict = False
    dimensionality = '[velocity]'


class Viscosity(PhysicalDimension):
    """
    A measure of a fluid's resistance to deformation at a given rate. The unit commonly used in the SI unit system
    is the poise (P).

    See Also:
        `Wikipedia: Viscosity <https://en.wikipedia.org/wiki/Viscosity>`_
    """
    strict = False
    dimensionality = '[viscosity]'


class Volume(PhysicalDimension):
    """
    A measure of three-dimensional space. In SI units, it is usually measured in cubic meters (m3).

    See Also:
        `Wikipedia: Volume <https://en.wikipedia.org/wiki/Volume>`_
    """
    strict = False
    dimensionality = '[volume]'


class VolumetricFlowRate(PhysicalDimension):
    """
    The volume of fluid that passes per unit time. It is also known as volume flow rate, or volume velocity. In SI
    units, it is usually measured in cubic metres per second (m3/s).

    See Also:
        `Wikipedia: Volumetric flow rate <https://en.wikipedia.org/wiki/Volumetric_flow_rate>`_
    """
    strict = False
    dimensionality = '[volumetric_flow_rate]'


class WaveNumber(PhysicalDimension):
    """
    The spatial frequency of a wave, measured in cycles per unit distance. SI units, it is usually measured in
    reciprocal of meters (1/m).

    See Also:
        `Wikipedia: Wavenumber <https://en.wikipedia.org/wiki/Wavenumber>`_
    """
    strict = False
    dimensionality = '[wavenumber]'
