//******************************************************************************
//
// File:    EmptyObjectBuf.java
// Package: benchmarks.detinfer.pj.edu.ritmp.buf
// Unit:    Class benchmarks.detinfer.pj.edu.ritmp.buf.EmptyObjectBuf
//
// This Java source file is copyright (C) 2007 by Alan Kaminsky. All rights
// reserved. For further information, contact the author, Alan Kaminsky, at
// ark@cs.rit.edu.
//
// This Java source file is part of the Parallel Java Library ("PJ"). PJ is free
// software; you can redistribute it and/or modify it under the terms of the GNU
// General Public License as published by the Free Software Foundation; either
// version 3 of the License, or (at your option) any later version.
//
// PJ is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
// A PARTICULAR PURPOSE. See the GNU General Public License for more details.
//
// A copy of the GNU General Public License is provided in the file gpl.txt. You
// may also obtain a copy of the GNU General Public License on the World Wide
// Web at http://www.gnu.org/licenses/gpl.html.
//
//******************************************************************************

package benchmarks.detinfer.pj.edu.ritmp.buf;

import benchmarks.detinfer.pj.edu.ritmp.Buf;
import benchmarks.detinfer.pj.edu.ritmp.ObjectBuf;

import benchmarks.detinfer.pj.edu.ritpj.reduction.ObjectOp;
import benchmarks.detinfer.pj.edu.ritpj.reduction.Op;

/**
 * Class EmptyObjectBuf provides an object buffer that contains no items for
 * messages using the Message Protocol (MP). When a message is sent from an
 * EmptyObjectBuf, the message item type is Object and the message length is 0.
 * When a message is received into an EmptyObjectBuf, the message item type must
 * be Object, but all items in the message are discarded.
 *
 * @author  Alan Kaminsky
 * @version 03-Jul-2008
 */
public class EmptyObjectBuf
	extends ObjectBuf<Object>
	{

// Exported constructors.

	/**
	 * Construct a new empty object buffer.
	 */
	public EmptyObjectBuf()
		{
		super (0);
		}

// Exported operations.

	/**
	 * Obtain the given item from this buffer.
	 * <P>
	 * The <TT>get()</TT> method must not block the calling thread; if it does,
	 * all message I/O in MP will be blocked.
	 *
	 * @param  i  Item index in the range 0 .. <TT>length()</TT>-1.
	 *
	 * @return  Item at index <TT>i</TT>.
	 */
	public Object get
		(int i)
		{
		throw new IndexOutOfBoundsException();
		}

	/**
	 * Store the given item in this buffer.
	 * <P>
	 * The <TT>put()</TT> method must not block the calling thread; if it does,
	 * all message I/O in MP will be blocked.
	 *
	 * @param  i     Item index in the range 0 .. <TT>length()</TT>-1.
	 * @param  item  Item to be stored at index <TT>i</TT>.
	 */
	public void put
		(int i,
		 Object item)
		{
		throw new IndexOutOfBoundsException();
		}

	/**
	 * Copy items from the given buffer to this buffer. The number of items
	 * copied is this buffer's length or <TT>theSrc</TT>'s length, whichever is
	 * smaller. If <TT>theSrc</TT> is this buffer, the <TT>copy()</TT> method
	 * does nothing.
	 *
	 * @param  theSrc  Source of items to copy into this buffer.
	 *
	 * @exception  ClassCastException
	 *     (unchecked exception) Thrown if <TT>theSrc</TT>'s item data type is
	 *     not the same as this buffer's item data type.
	 */
	public void copy
		(Buf theSrc)
		{
		}

	/**
	 * Create a buffer for performing parallel reduction using the given binary
	 * operation. The results of the reduction are placed into this buffer.
	 * <P>
	 * Operations performed on the returned reduction buffer have the same
	 * effect as operations performed on this buffer, except whenever a source
	 * item <I>S</I> is put into a destination item <I>D</I> in this buffer,
	 * <I>D</I> is set to <I>D op S</I>, that is, the reduction of <I>D</I> and
	 * <I>S</I> using the given binary operation (rather than just setting
	 * <I>D</I> to <I>S</I>).
	 *
	 * @param  op  Binary operation.
	 *
	 * @exception  ClassCastException
	 *     (unchecked exception) Thrown if this buffer's element data type and
	 *     the given binary operation's argument data type are not the same.
	 */
	public Buf getReductionBuf
		(Op op)
		{
		ObjectOp objectop = (ObjectOp) op;
		return this;
		}

	}
