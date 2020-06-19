#include <Python.h>
#include <math.h>

/* TODO delete or document this
 *
 */
static PyObject* py_combine(PyObject* self, PyObject* args)
{
	const unsigned char *im_bg;
	const unsigned char *im_fg;
	int size;

	int i;
	long int sum;
	int area;

	if (!PyArg_ParseTuple(args, "s#s#", &im_bg, &size, &im_fg, &size)) return NULL;

	sum = 0;
	area = 0;
	for (i=0; i < size; i++) {
		if (im_fg[i]){
			sum += im_bg[i];
			area++;
		}
	}

	return Py_BuildValue("d", ((double) sum) / area);
}

/* Hough transform
 *
 * Takes dimentions of the image, the image, initial angle and TODO dt is what?.
 * Computes Hough transform of the image. TODO size etc.
 *
 */
static PyObject* py_hough(PyObject* self, PyObject* args)
{
	const unsigned char *image;
	int x;
	int y;
	int size;
	double init_angle;
	double dt;

	int i;
	int j;
	int a;

	double distance;
	int column;
	int minimum;
	int maximum;

	int *matrix;
	unsigned char *n_image;
	PyObject *result;

	if (!PyArg_ParseTuple(args, "(ii)s#dd", &x, &y, &image, &size, &init_angle, &dt)) return NULL;
	// x and y are width and height of the image as ints
	// Python sends image as (byte)string and since it is not null-terminated, must send its size
	// init_angle and dt are doubles
	

	matrix = (int*) malloc(size * sizeof(int));
	for (i=0; i < x * y; i++) {
		matrix[i] = 0;
	}



	for (i=0; i < x; i++) {
		for (j=0; j < y; j++) {
			if (image[j * x + i]){
				for (a=0; a < y; a++){
					distance = (((i - x / 2) * sin((dt * a) + init_angle)) +
							((j - y / 2) * -cos((dt * a) + init_angle)) +
							x / 2);
					column = (int) round(distance);
					if ((0 <= column) && (column < x)){
						matrix[a * x + column]++;
					}
				}
			}
		}
	}
	



	n_image = (char*) malloc(size * sizeof(char));
	minimum = matrix[0];
	maximum = matrix[0];
	for (i=1; i < x * y; i++){
		if (matrix[i] < minimum) minimum = matrix[i];
		if (matrix[i] > maximum) maximum = matrix[i];
	}
	maximum = maximum - minimum + 1;
	for (i=0; i < x * y; i++){
		n_image[i] = (char) ((((float) (matrix[i] - minimum)) / maximum) * 256);
	}

	free(matrix);

	result = Py_BuildValue("s#", n_image, size);
	free(n_image);
	return result;
}

/* Edge detection
 *
 * Takes image size, the image, and the size of TODO what?
 */
static PyObject* py_edge(PyObject* self, PyObject* args)
{
	const unsigned char *image;
	int x;
	int y;
	int size;

	int i;
	int j;
	int sum;

	unsigned char *n_image;
	PyObject *result;

	if (!PyArg_ParseTuple(args, "(ii)s#", &x, &y, &image, &size)) return NULL;
	// x and y are width and height of the image as ints
	// Python sends image as (byte)string and since it is not null-terminated, must send its size

	n_image = (char*) malloc(size);
	for (i=0; i < 2 * x; i++) {
		n_image[i] = 0;
		n_image[(y - 2) * x + i] = 0;
	}
	for (i=0; i < y; i++) {
		n_image[x * i] = 0;
		n_image[x * i + 1] = 0;
		n_image[x * i + x - 2] = 0;
		n_image[x * i + x - 1] = 0;
	}



	for (i=2; i < x - 2; i++) {
		for (j=2; j < y - 2; j++) {
			sum = image[x * j + i - 2] + image[x * j + i - 1] + image[x * j + i + 1] + image[x * j + i + 2] + 
				image[x * (j - 2) + i - 2] + image[x * (j - 2) + i - 1] + image[x * (j - 2) + i] + 
				image[x * (j - 2) + i + 1] + image[x * (j - 2) + i + 2] + 
				image[x * (j - 1) + i - 2] + image[x * (j - 1) + i - 1] + image[x * (j - 1) + i] + 
				image[x * (j - 1) + i + 1] + image[x * (j - 1) + i + 2] +
				image[x * (j + 2) + i - 2] + image[x * (j + 2) + i - 1] + image[x * (j + 2) + i] + 
				image[x * (j + 2) + i + 1] + image[x * (j + 2) + i + 2] +
				image[x * (j + 1) + i - 2] + image[x * (j + 1) + i - 1] + image[x * (j + 1) + i] + 
				image[x * (j + 1) + i + 1] + image[x * (j + 1) + i + 2] 
				- (24 * image[x * j + i]);
			if (sum < 0) sum = 0;
			if (sum > 255) sum = 255;
			n_image[x * j + i] = sum;
		}
	}



	result = Py_BuildValue("s#", n_image, size);
	free(n_image);
	return result;
}

static PyMethodDef pcf_methods[] = {
	{"combine", py_combine, METH_VARARGS},
	{"edge", py_edge, METH_VARARGS},
	{"hough", py_hough, METH_VARARGS},
	{NULL, NULL}
};

static struct PyModuleDef pcf_def = {
        PyModuleDef_HEAD_INIT,
        "pcf",     			   /* m_name */
        "Performance Critical Functions",  /* m_doc */
        -1,                  		   /* m_size */
        pcf_methods,    		   /* m_methods */
};

PyMODINIT_FUNC PyInit_pcf(void) {
    Py_Initialize();
    return PyModule_Create(&pcf_def);
}
